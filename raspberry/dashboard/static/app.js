const VIAS = [
    "A",
    "B",
    "C",
    "D"
];


let ultimaVersaoImagem = null;


// =====================================================
// CRIAR CARDS
// =====================================================

function criarCards() {

    const grid =
        document.getElementById(
            "vias-grid"
        );


    grid.innerHTML = "";


    VIAS.forEach(via => {

        grid.innerHTML += `

        <section
            class="via-card"
            id="card-${via}"
        >

            <div class="via-title">

                <h2>
                    Via ${via}
                </h2>

                <span
                    class="via-state"
                    id="estado-${via}"
                >
                    -
                </span>

            </div>


            <div class="traffic-light">

                <div
                    id="${via}-vermelho"
                    class="light red"
                ></div>

                <div
                    id="${via}-amarelo"
                    class="light yellow"
                ></div>

                <div
                    id="${via}-verde"
                    class="light green"
                ></div>

            </div>


            <div class="via-data">

                <div>

                    <span>
                        Veículos
                    </span>

                    <strong
                        id="veiculos-${via}"
                    >
                        —
                    </strong>

                </div>


                <div>

                    <span>
                        Congestionamento
                    </span>

                    <strong
                        id="congestionamento-${via}"
                    >
                        —
                    </strong>

                </div>


                <div>

                    <span>
                        Prioritário
                    </span>

                    <strong
                        id="prioritario-${via}"
                    >
                        —
                    </strong>

                </div>


                <div>

                    <span>
                        Tempo de espera
                    </span>

                    <strong
                        id="espera-${via}"
                    >
                        —
                    </strong>

                </div>

            </div>

        </section>
        `;
    });
}


// =====================================================
// STATUS DOS COMPONENTES
// =====================================================

function atualizarStatus(
    id,
    valor
) {

    const elemento =
        document.getElementById(
            id
        );


    if (!elemento) {

        return;
    }


    elemento.classList.remove(
        "online",
        "offline",
        "waiting"
    );


    if (
        valor === true
    ) {

        elemento.classList.add(
            "online"
        );

    } else if (
        valor === false
    ) {

        elemento.classList.add(
            "offline"
        );

    } else {

        elemento.classList.add(
            "waiting"
        );
    }
}


// =====================================================
// SEMÁFORO
// =====================================================

function atualizarSemaforo(
    via,
    estado
) {

    const cores = [
        "vermelho",
        "amarelo",
        "verde"
    ];


    cores.forEach(cor => {

        const elemento =
            document.getElementById(
                `${via}-${cor}`
            );


        if (elemento) {

            elemento
                .classList
                .remove(
                    "active"
                );
        }
    });


    if (
        cores.includes(
            estado
        )
    ) {

        const luz =
            document.getElementById(
                `${via}-${estado}`
            );


        if (luz) {

            luz
                .classList
                .add(
                    "active"
                );
        }
    }


    const label =
        document.getElementById(
            `estado-${via}`
        );


    if (label) {

        label.textContent = (
            estado
            ?
            estado.toUpperCase()
            :
            "-"
        );
    }


    const card =
        document.getElementById(
            `card-${via}`
        );


    if (card) {

        card.classList.toggle(

            "green-active",

            estado === "verde"
        );
    }
}


// =====================================================
// IMAGEM DO YOLO
// =====================================================

function atualizarImagemYolo(
    versao
) {

    const imagem =
        document.getElementById(
            "imagem-yolo"
        );


    if (!imagem) {

        return;
    }


    if (!versao) {

        return;
    }


    // Não baixa novamente a mesma imagem.
    if (
        ultimaVersaoImagem
        === versao
    ) {

        return;
    }


    ultimaVersaoImagem =
        versao;


    imagem.src =
        "/api/imagem-yolo"
        +
        "?v="
        +
        encodeURIComponent(
            versao
        );
}


// =====================================================
// ATUALIZAR TELA
// =====================================================

function atualizarTela(
    dados
) {

    atualizarStatus(
        "status-bluetooth",
        dados.sistema.bluetooth
    );


    atualizarStatus(
        "status-camera",
        dados.sistema.camera
    );


    atualizarStatus(
        "status-yolo",
        dados.sistema.yolo
    );


    atualizarStatus(
        "status-fpga",
        dados.sistema.fpga
    );


    // =================================================
    // RESUMO
    // =================================================

    const viaAberta =
        document.getElementById(
            "via-aberta"
        );


    if (viaAberta) {

        viaAberta.textContent = (

            dados.via_aberta
            ===
            "X"

            ?
            "Nenhuma"

            :
            `Via ${dados.via_aberta}`
        );
    }


    const ultimaDeteccao =
        document.getElementById(
            "ultima-deteccao"
        );


    if (ultimaDeteccao) {

        ultimaDeteccao.textContent = (

            dados.ultima_deteccao

            ?
            `Via ${dados.ultima_deteccao}`

            :
            "Nenhuma"
        );
    }


    const ultimaAtualizacao =
        document.getElementById(
            "ultima-atualizacao"
        );


    if (ultimaAtualizacao) {

        ultimaAtualizacao.textContent =

            dados.ultima_atualizacao

            ||
            "-";
    }


    // =================================================
    // VIAS
    // =================================================

    VIAS.forEach(via => {

        const dadosVia =
            dados.vias[
                via
            ];


        if (!dadosVia) {

            return;
        }


        atualizarSemaforo(
            via,
            dadosVia.semaforo
        );


        const veiculos =
            document.getElementById(
                `veiculos-${via}`
            );


        if (veiculos) {

            veiculos.textContent =

                dadosVia.veiculos

                ??
                "—";
        }


        const congestionamento =
            document.getElementById(
                `congestionamento-${via}`
            );


        if (congestionamento) {

            congestionamento.textContent =

                dadosVia.congestionamento

                ??
                "Aguardando YOLO";
        }


        const prioritario =
            document.getElementById(
                `prioritario-${via}`
            );


        if (prioritario) {

            prioritario.textContent =

                dadosVia
                    .veiculo_prioritario

                ?
                (
                    dadosVia
                        .tipo_prioritario

                    ??
                    "Detectado"
                )

                :
                "Nenhum";
        }


        const espera =
            document.getElementById(
                `espera-${via}`
            );


        if (espera) {

            espera.textContent =

                dadosVia
                    .tempo_espera
                !==
                null

                ?
                `${dadosVia.tempo_espera}s`

                :
                "—";
        }
    });


    // =================================================
    // IMAGEM
    // =================================================

    atualizarImagemYolo(
        dados.ultima_atualizacao
    );
}


// =====================================================
// BUSCAR ESTADO
// =====================================================

async function carregarEstado() {

    try {

        const resposta =
            await fetch(

                "/api/status",

                {
                    cache:
                        "no-store"
                }
            );


        if (!resposta.ok) {

            throw new Error(
                "API indisponível"
            );
        }


        const dados =
            await resposta.json();


        atualizarTela(
            dados
        );

    } catch (erro) {

        console.error(

            "Erro ao atualizar dashboard:",

            erro
        );
    }
}


// =====================================================
// INICIAR
// =====================================================

criarCards();

carregarEstado();


// Dados continuam atualizando rapidamente.
setInterval(
    carregarEstado,
    500
);
