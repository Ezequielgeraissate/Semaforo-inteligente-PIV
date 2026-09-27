#include <Arduino.h>
#include "esp_camera.h"
#include <WiFi.h>
#include "esp_http_server.h"
#include "soc/soc.h"
#include "soc/rtc_cntl_reg.h"

// =====================================================
// AJUSTES RAPIDOS
// =====================================================

#define XCLK_HZ            8000000     // tente 8000000, 10000000 ou 16000000
#define FRAME_INICIAL      FRAMESIZE_QVGA
#define QUALIDADE_JPEG     12          // maior numero = mais compressao
#define DESATIVAR_BROWNOUT 1           // 1 = diagnostico (veja nota abaixo)
#define POTENCIA_WIFI      WIFI_POWER_8_5dBm

// =====================================================
// WIFI
// =====================================================

const char* ssid     = "MORUMBI";
const char* password = "trimundial2005";

// =====================================================
// PINOS - AI THINKER ESP32-CAM
// =====================================================

#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27

#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5

#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

// =====================================================
// PAGINA WEB
// =====================================================

const char paginaHTML[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ESP32-CAM</title>
<style>
body { font-family: Arial; text-align: center; background: #eeeeee; }
button, select { padding: 12px 20px; font-size: 18px; }
img { margin-top: 20px; max-width: 95%; }
</style>
</head>
<body>
<h1>ESP32-CAM</h1>
<select id="tam">
  <option value="qvga">QVGA 320x240</option>
  <option value="vga">VGA 640x480</option>
  <option value="svga">SVGA 800x600</option>
</select>
<button onclick="capturar()">Capturar imagem</button>
<br>
<img id="foto">
<script>
function capturar() {
  const t = document.getElementById("tam").value;
  document.getElementById("foto").src =
    "/capture?size=" + t + "&t=" + Date.now();
}
</script>
</body>
</html>
)rawliteral";

// =====================================================
// AUXILIARES
// =====================================================

// JPEG integro: comeca com FFD8 e termina com FFD9
bool jpegValido(camera_fb_t *fb) {
  if (fb == NULL || fb->len < 500) return false;
  if (fb->buf[0] != 0xFF || fb->buf[1] != 0xD8) return false;
  if (fb->buf[fb->len - 2] != 0xFF || fb->buf[fb->len - 1] != 0xD9) return false;
  return true;
}

framesize_t tamanhoDoTexto(const char *s) {
  if (strcmp(s, "vga")  == 0) return FRAMESIZE_VGA;
  if (strcmp(s, "svga") == 0) return FRAMESIZE_SVGA;
  return FRAMESIZE_QVGA;
}

// =====================================================
// HANDLERS
// =====================================================

static esp_err_t paginaHandler(httpd_req_t *req) {
  httpd_resp_set_type(req, "text/html");
  return httpd_resp_send(req, paginaHTML, HTTPD_RESP_USE_STRLEN);
}

static esp_err_t capturaHandler(httpd_req_t *req) {

  // Le o parametro ?size=
  char query[64], valor[16];
  sensor_t *sensor = esp_camera_sensor_get();

  if (httpd_req_get_url_query_str(req, query, sizeof(query)) == ESP_OK &&
      httpd_query_key_value(query, "size", valor, sizeof(valor)) == ESP_OK) {
    framesize_t novo = tamanhoDoTexto(valor);
    if (sensor && sensor->status.framesize != novo) {
      sensor->set_framesize(sensor, novo);
      delay(300);   // deixa o sensor assentar
    }
  }

  // Descarta um frame possivelmente antigo
  camera_fb_t *velho = esp_camera_fb_get();
  if (velho) esp_camera_fb_return(velho);
  delay(30);

  camera_fb_t *fb = NULL;
  const int MAX_TENTATIVAS = 5;

  for (int i = 0; i < MAX_TENTATIVAS; i++) {
    fb = esp_camera_fb_get();

    if (fb == NULL) {
      Serial.println("ERRO: falha ao capturar.");
      delay(50);
      continue;
    }

    if (jpegValido(fb)) break;

    Serial.printf("Frame ruim (%u bytes), tentativa %d/%d\n",
                  (unsigned)fb->len, i + 1, MAX_TENTATIVAS);
    esp_camera_fb_return(fb);
    fb = NULL;
    delay(80);
  }

  if (fb == NULL) {
    httpd_resp_send_500(req);
    return ESP_FAIL;
  }

  Serial.printf("Captura: %dx%d | %u bytes\n",
                fb->width, fb->height, (unsigned)fb->len);

  httpd_resp_set_type(req, "image/jpeg");
  httpd_resp_set_hdr(req, "Cache-Control",
                     "no-store, no-cache, must-revalidate, max-age=0");
  httpd_resp_set_hdr(req, "Pragma", "no-cache");
  httpd_resp_set_hdr(req, "Expires", "0");

  esp_err_t r = httpd_resp_send(req, (const char *)fb->buf, fb->len);

  esp_camera_fb_return(fb);
  return r;
}

// =====================================================
// SERVIDOR
// =====================================================

void iniciarServidor() {

  httpd_config_t config = HTTPD_DEFAULT_CONFIG();
  config.stack_size = 8192;
  httpd_handle_t servidor = NULL;

  httpd_uri_t pagina = {
    .uri = "/", .method = HTTP_GET,
    .handler = paginaHandler, .user_ctx = NULL
  };

  httpd_uri_t captura = {
    .uri = "/capture", .method = HTTP_GET,
    .handler = capturaHandler, .user_ctx = NULL
  };

  if (httpd_start(&servidor, &config) == ESP_OK) {
    httpd_register_uri_handler(servidor, &pagina);
    httpd_register_uri_handler(servidor, &captura);
    Serial.println("Servidor HTTP iniciado.");
  }
}

// =====================================================
// SETUP
// =====================================================

void setup() {

#if DESATIVAR_BROWNOUT
  // Diagnostico: se melhorar com isso, o problema e ENERGIA.
  WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0);
#endif

  Serial.begin(115200);
  Serial.setDebugOutput(false);   // logs internos atrapalham a temporizacao
  delay(1000);
  Serial.println("\nInicializando ESP32-CAM...");

  // ---------------- CAMERA (antes do Wi-Fi) ----------------
  camera_config_t config = {};

  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer   = LEDC_TIMER_0;

  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;

  config.pin_xclk  = XCLK_GPIO_NUM;
  config.pin_pclk  = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href  = HREF_GPIO_NUM;

  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;

  config.pin_pwdn  = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;

  config.xclk_freq_hz = XCLK_HZ;
  config.pixel_format = PIXFORMAT_JPEG;
  config.frame_size   = FRAME_INICIAL;
  config.jpeg_quality = QUALIDADE_JPEG;

  // Um unico buffer, captura sob demanda:
  // evita a camera escrevendo na PSRAM o tempo todo enquanto o Wi-Fi roda
  config.fb_count   = 1;
  config.grab_mode  = CAMERA_GRAB_WHEN_EMPTY;

  if (psramFound()) {
    Serial.println("PSRAM encontrada.");
    config.fb_location = CAMERA_FB_IN_PSRAM;
  } else {
    Serial.println("ATENCAO: PSRAM nao encontrada.");
    config.fb_location = CAMERA_FB_IN_DRAM;
    config.frame_size  = FRAMESIZE_QVGA;
  }

  esp_err_t erro = esp_camera_init(&config);
  if (erro != ESP_OK) {
    Serial.printf("ERRO ao iniciar camera: 0x%x\n", erro);
    return;
  }
  Serial.println("Camera inicializada.");

  sensor_t *sensor = esp_camera_sensor_get();
  if (sensor == NULL) {
    Serial.println("ERRO ao acessar sensor.");
    return;
  }

  sensor->set_brightness(sensor, 0);
  sensor->set_contrast(sensor, 0);
  sensor->set_saturation(sensor, 0);
  sensor->set_whitebal(sensor, 1);
  sensor->set_awb_gain(sensor, 1);
  sensor->set_exposure_ctrl(sensor, 1);
  sensor->set_aec2(sensor, 1);
  sensor->set_gain_ctrl(sensor, 1);

  // Estabiliza exposicao e balanco de branco
  delay(500);
  for (int i = 0; i < 8; i++) {
    camera_fb_t *fb = esp_camera_fb_get();
    if (fb) esp_camera_fb_return(fb);
    delay(120);
  }

  // ---------------- WIFI ----------------
  WiFi.mode(WIFI_STA);
  WiFi.setSleep(false);
  WiFi.begin(ssid, password);
  WiFi.setTxPower(POTENCIA_WIFI);

  Serial.print("Conectando ao Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWi-Fi conectado.");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());

  // ---------------- SERVIDOR ----------------
  iniciarServidor();

  Serial.println("==============================");
  Serial.print("Abra no navegador: http://");
  Serial.println(WiFi.localIP());
  Serial.println("==============================");
}

void loop() {
  delay(10000);
}
