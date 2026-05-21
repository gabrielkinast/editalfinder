var $prestador = 'legalle';

$(document).ready(function() {
    
    var $dOut = $('#date');
    var months = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'];
    var days = ['Domingo', 'Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira', 'Sábado'];

    function update() {
        var date = new Date();

        // var hours = date.getHours() < 10 ? '0' + date.getHours() : date.getHours();
        //
        // var minutes = date.getMinutes() < 10 ? '0' + date.getMinutes() : date.getMinutes();
        //
        // var seconds = date.getSeconds() < 10 ? '0' + date.getSeconds() : date.getSeconds();

        var dayOfWeek = days[date.getDay()];
        var month = months[date.getMonth()];
        var day = date.getDate();
        var year = date.getFullYear();

        var dateString = dayOfWeek + ', ' + day + ' de ' + month + ' de ' + year;

        $dOut.text(dateString);
        // $hOut.text(hours);
        // $mOut.text(minutes);
        // $sOut.text(seconds);
    }

    update();
    window.setInterval(update, 1000);
    
    if(typeof $('#input-open-default-list').val()!='undefined') {
        $('a[href="' + $('#input-open-default-list').val() + '"]').tab('show');
    }

    function getFilteredEditais(filtro) {
        $('.header-loader').removeClass('d-none');
        $.getJSON($WS_URL+"editais/" + filtro, function(data) {
            $('#editais_lista span').remove();
            if (data['editais'] == null) {
                $('#editais_lista').html('<div class="col-sm-12 border border-base rounded mb-4">' +
                    '                       <div class="py-4">\n' +
                    '                            <div class="row">\n' +
                    '                                <div class="col-md-6 offset-md-3 text-center text-base">\n' +
                    '                                    <h1 class="text-400"><i class="fe fe-alert-circle"></i></h1>\n' +
                    '                                    <p class="text-700 text-16">NENHUM CONCURSO OU PROCESSO SELETIVO ENCONTRADO PARA ESTE FILTRO</p>\n' +
                    '                                </div>\n' +
                    '                            </div>\n' +
                    '                        </div>' +
                    '                      </div>');
            } else {
                $('#termo').html('"' + filtro + '"');
                $("#status_editais").html('Cancursos e Seletivos');

                var $edital = '<div class="list-group list-group-flush">';
                var $link ='';
                var i = 0;
                $.each(data.editais, function(key, val) {

                    i = parseInt(i) + 1;

                    var $inicio = val['EdiInicioInscricoes'].split(" ");
                    var $final = val['EdiFimInscricoes'].split(" ");

                    if (val['EdiStatus']=='2') {
                        $link = '<div class="col-lg-3 col-md-3 text-center text-12 text-500 yellow lighten-5 py-5 h-100">\n' +
                            '            <div class="w-100">\n' +
                            '                 <b class="text-13">PERÍODO DE INSCRIÇÕES</b><br>\n' +
                            '                 <b class="text-muted">INÍCIO:</b> '+$inicio[0]+' '+$inicio[1]+'<br>\n' +
                            '                 <b class="text-muted">TÉRMINO:</b> '+$final[0]+' '+$final[1]+'<br>\n' +
                            '                 <a class="btn btn-yellow text-700 mt-2" href="'+$CANDIDATO_URL+'inscricao/'+val['EdiLink']+'" target="_blank">INSCREVA-SE</a>\n' +
                            '             </div>\n' +
                            '         </div>';
                    } else if (val['EdiStatus']=='3') {
                        $link = '<div class="col-lg-3 col-md-3 text-center text-12 text-500 yellow lighten-5 h-100 py-5 text-12">\n' +
                            '            <div class="w-100">\n' +
                            '                 <b class="text-13">PERÍODO DE INSCRIÇÕES</b><br>\n' +
                            '                 <b class="text-muted">INÍCIO:</b> '+$inicio[0]+' '+$inicio[1]+'<br>\n' +
                            '                 <b class="text-muted">TÉRMINO:</b> '+$final[0]+' '+$final[1]+'<br>\n' +
                            '                 <a class="btn btn-yellow btn-sm disabled text-500 mt-2" href="javascript:void(0)">FORA DO PERÍODO</a>\n' +
                            '             </div>\n' +
                            '         </div>';
                    } else if (val['EdiStatus']=='4') {
                        $link = '<div class="col-lg-3 col-md-3 text-center text-12 text-500 yellow lighten-5 h-100 py-5 text-12">\n' +
                            '            <div class="w-100">\n' +
                            '                 <b class="text-13">PERÍODO DE INSCRIÇÕES</b><br>\n' +
                            '                 <b class="text-muted">INÍCIO:</b> '+$inicio[0]+' '+$inicio[1]+'<br>\n' +
                            '                 <b class="text-muted">TÉRMINO:</b> '+$final[0]+' '+$final[1]+'<br>\n' +
                            '                 <a class="btn btn-yellow btn-sm disabled text-500 mt-2" href="javascript:void(0)">EDITAL ENCERRADO</a>\n' +
                            '             </div>\n' +
                            '         </div>';
                    } else if (val['EdiStatus']=='1') {
                        $link = '<div class="col-lg-3 col-md-3 text-center text-12 text-500 yellow lighten-5 h-100 py-5 text-12">\n' +
                            '            <div class="w-100">\n' +
                            '                 <b class="text-13">PERÍODO DE INSCRIÇÕES</b><br>\n' +
                            '                 <b class="text-muted">INÍCIO:</b> Previsto<br>\n' +
                            '                 <b class="text-muted">TÉRMINO:</b> Previsto<br>\n' +
                            '                 <a class="btn btn-yellow btn-sm disabled text-500 mt-2" href="javascript:void(0)">AGUARDANDO INÍCIO</a>\n' +
                            '             </div>\n' +
                            '         </div>';
                    }
                    if( /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ) {
                        $edital += ' <div class="list-group-item border-0">\n' +
                            '                    <div class="row no-gutters align-items-center grey lighten-4">\n' +
                            '                        <div class="col-12 text-center my-2 my-md-0">\n' +
                            '                            <img src="'+$MIDIAS_URL+'entidade/' + val['EntLogo'] + '" class="img-responsive mx-auto" style="max-width:150px; max-height: 60px; border-radius: 5px;">\n' +
                            '                            <p class="m-0 text-12 px-2">\n' +
                            '                                <span class="text-14 text-700">' + val['TipNome'] + ' <small>' + val['EdiNumero'] + '</small></span><br>\n' +
                            '                                ' + val['EntNome'] + '\n' +
                            '                            </p>\n' +
                            '                        </div>\n' +
                            '                        <div class="col-12 text-center">\n' +
                            '                        <div class="btn-group-vertical btn-group-lg my-4">\n' +
                            '                            <a href="javascript:void(0)" data-id="' + val['EdiLink'] + '" class="btn btn-outline-base py-3 btn-ver-edital text-10 text-500">\n' +
                            '                                <i class="fa fa-file-alt"></i> VER EDITAL\n' +
                            '                            </a>\n' +
                            '                            <a href="javascript:void(0)" data-id="' + val['EdiLink'] + '" class="btn btn-outline-base py-3 btn-block btn-ver-material-estudo text-10 text-500">\n' +
                            '                                <i class="fa fa-copy"></i> LEGISLAÇÃO\n' +
                            '                            </a>\n' +
                            '                            <a href="' + $BASE_URL + 'editais/ver/' + val['EdiLink'] + '" class="btn btn-outline-base py-3 btn-block text-10 text-500">\n' +
                            '                                <i class="fa fa-plus-square"></i> MAIS DETALHES\n' +
                            '                            </a>\n' +
                            '                        </div>\n' +
                            '                        </div>\n' + $link +
                            '                    </div>\n' +
                            '                </div>';
                    }else {
                        $edital += ' <div class="list-group-item border-0">\n' +
                            '                    <div class="row no-gutters align-items-center grey lighten-4">\n' +
                            '                        <div class="col-lg-3 col-md-12 text-center my-2 my-md-0">\n' +
                            '                            <img src="'+$MIDIAS_URL+'entidade/' + val['EntLogo'] + '" class="img-responsive mx-auto mt-4" style="max-width:150px; max-height: 60px; border-radius: 5px;">\n' +
                            '                            <p class="m-0 text-12 px-2">\n' +
                            '                                <span class="text-14 text-700">' + val['TipNome'] + ' <small>' + val['EdiNumero'] + '</small></span><br>\n' +
                            '                                ' + val['EntNome'] + '\n' +
                            '                            </p>\n' +
                            '                        </div>\n' +
                            '                        <div class="col-lg-2 col-md-3 text-center pt-2">\n' +
                            '                            <a href="javascript:void(0)" data-id="' + val['EdiLink'] + '" class="btn btn-outline-base btn-ver-edital border-secondary btn-sm w-75 text-10 text-500 py-3">\n' +
                            '                                VER<br>EDITAL<br>\n' +
                            '                                <i class="fa fa-file-alt fa-3x mt-3"></i>\n' +
                            '                            </a>\n' +
                            '                        </div>\n' +
                            '                        <div class="col-lg-2 col-md-3 text-center pt-2">\n' +
                            '                            <a href="javascript:void(0)" id="' + val['EdiLink'] + '" class="btn btn-outline-base border-secondary btn-ver-material-estudo btn-sm w-75 text-10 text-500 py-3">\n' +
                            '                                <br>LEGISLAÇÃO<br>\n' +
                            '                                <i class="fa fa-copy fa-3x mt-3"></i>\n' +
                            '                            </a>\n' +
                            '                        </div>\n' +
                            '                        <div class="col-lg-2 col-md-3 text-center pt-2">\n' +
                            '                            <a href="' + $BASE_URL + 'editais/ver/' + val['EdiLink'] + '" class="btn btn-outline-base border-secondary btn-sm w-75 text-10 text-500 py-3">\n' +
                            '                                MAIS<br>DETALHES<br>\n' +
                            '                                <i class="fa fa-plus-square fa-3x mt-3"></i>\n' +
                            '                            </a>\n' +
                            '                        </div>\n' + $link +
                            '                    </div>\n' +
                            '                </div>';
                    }
                });

                $('#editais_lista').html(($edital+'</div>'));
                $('#resultados').html(i);
            }
        }).done(function(){
            $('.header-loader').addClass('d-none');
        }).error(function() {
            $('.header-loader').addClass('d-none');
            $('#editais_lista').append('<div class="box-content box-content-1 border-box-content-left bg-color-light color-dark text-uppercase">Ocorreu um erro em sua pesquisa. Por favor, reveja os termos digitados.</div>');
        });
    }

    $(document).ready(function() {
        if (typeof $('#filtered-editais') == 'undefined' || $('#filtered-editais').val() === 'true' || $('#filtered-editais').length > 0) {
            getFilteredEditais($('#filtered').val());
        }
    });

    function getEdital(edital, prestador) {
        $('.header-loader').removeClass('d-none');
        $.getJSON($WS_URL+"editais/edital/" + edital, function(data) {
            if (data['edital'] == null) {
                window.location = $BASE_URL+"erro404";
            } else {
                if (data.edital[0].EdiStatus==='1') {
                    $('#btn-inscricao').html('<i class="fe fe-alert-triangle"></i> Fora do período de inscrição').attr('href', 'javascript:void(0)').addClass('disabled');
                    $('#div-inscricao').removeClass('green').addClass('blue')
                } else if (data.edital[0].EdiStatus==='2') {
                    $('#btn-inscricao').html('<i class="fe fe-edit-2"></i> Realizar inscrição').attr('href', $CANDIDATO_URL+'inscricao/' + data.edital[0].EdiLink).attr('target', '_blank').attr('title', 'Clique para realizar a inscrição');
                } else if (data.edital[0].EdiStatus==='3') {
                    $('#btn-inscricao').html('<i class="fe fe-alert-triangle"></i> Inscrições finalizadas').attr('href', 'javascript:void(0)').attr('title', 'Inscrições finalizadas').addClass('disabled');
                    $('#div-inscricao').removeClass('green').addClass('yellow')
                } else if (data.edital[0].EdiStatus==='4') {
                    $('#btn-inscricao').html('<i class="fe fe-check-circle"></i> Edital encerrado').attr('href', 'javascript:void(0)').attr('title', 'Edital encerrado').addClass('disabled');
                    $('#div-inscricao').removeClass('green').addClass('red')
                }
                $('.page-title').html(data.edital[0].TipNome + ' ' + data.edital[0].EdiNumero);
                if (data.edital[0].EdiObservacoes != "") {
                    $('#observacoes-edital').html('<div class="row"><div class="col-sm-12"><div class="alert alert-info"><h5 class="m-0"><i class="fa fa-quote-left fa-2x pull-left fa-border"></i> ' + data.edital[0].EdiObservacoes + '</h5></div></div></div>');
                }
                $('#validade-edital').html(data.edital[0].EntNome);

                // var inscricao = data.edital[0].EdiInicioInscricoes.split(" ");
                // var datainscricao = inscricao[0].split("-");
                // var inscricaofim = data.edital[0].EdiFimInscricoes.split(" ");
                // var datainscricaofim = inscricaofim[0].split("-");
                //
                // $('#inicio-inscricoes').html('<b>DATA:</b> '+datainscricao[2] + '/' + datainscricao[1] + '/' + datainscricao[0]+'<br><b>HORA:</b> '+inscricao[1][0]+inscricao[1][1]+':'+inscricao[1][3]+inscricao[1][4]);
                // $('#fim-inscricoes').html('<b>DATA:</b> '+datainscricaofim[2] + '/' + datainscricaofim[1] + '/' + datainscricaofim[0]+'<br><b>HORA:</b> '+inscricaofim[1][0]+inscricaofim[1][1]+':'+inscricaofim[1][3]+inscricaofim[1][4]);


                $('#tipo-edital').html(data.edital[0].TipNome);
                $('#validade-edital2').html(data.edital[0].EdiValidade + ' ano(s)');
                $('#responsavel-edital').html(data.edital[0].UsuentNome);
                $('#contato-edital').html(data.edital[0].UsuentFone);

                $('#edital-entidade').html('<span>' + data.edital[0].EntNome + '</span>');
                $('#logo-entidade').html('<img alt="" class="media-object img-responsive center-block w-100 mx-auto" src="' + data.edital[0].EntLogo + '">');
                $('#nome-entidade-edital').html(data.edital[0].EntNome).attr('title', data.edital[0].EntNome);
                $('#cidade-uf-entidade').html('<span class="status-icon bg-secondary"></span> ' + data.edital[0].CidNome + ' - ' + data.edital[0].EstSigla).attr('title', data.edital[0].CidNome + ' - ' + data.edital[0].EstSigla);
                $('#endereco-rua-entidade').html('<span class="status-icon bg-secondary"></span> ' + data.edital[0].EntRua + ', nº ' + data.edital[0].EntNumero).attr('title', data.edital[0].EntRua + ', nº ' + data.edital[0].EntNumero);
                $('#bairro-cep-entidade').html('<span class="status-icon bg-secondary"></span> ' + data.edital[0].EntBairro + ' / ' + data.edital[0].EntCep).attr('title', 'Bairro ' + data.edital[0].EntBairro + ' / CEP ' + data.edital[0].EntCep);
                $('#telefone-email-entidade').html('<span class="fa fa-phone fa-fw text-dark"></span> ' + data.edital[0].EntFone).attr('title', 'Telefone ' + data.edital[0].EntFone);

                if(data.edital[0].EdiObservacoes!=''){
                    $('#div-edi-observacoes').html('<i class="fa fa-quote-left fa-2x text-secondary"></i><br><div class="pl-5">'+data.edital[0].EdiObservacoes+'</div>').removeClass('d-none')
                }

                var $tr = '';
                if (data.modalidades_cargos != null) {
                    $.each(data.modalidades_cargos, function (key, val) {
                        $tr += '<tr>' +
                            '<td>'+val['CarNome']+'</td>' +
                            '<td class="text-center">'+(parseInt(val['CarVagas'])>0?val['CarVagas']:(parseInt(val['CarVagasReserva'])>0?('<span class="badge text-12 badge-pill badge-base">'+val['CarVagasReserva']+' reserva</span>'):'<span class="badge text-12 badge-pill badge-base">reserva</span>'))+'</td>' +
                            '<td class="text-center">R$ '+val['CarRemuneracao'].replace('.',',')+'</td>' +
                            '</tr>';
                    });
                } else {
                    $tr = '<tr class="red lighten-5"><td colspan="3" class="text-center py-3 text-danger">Nenhum cargo foi encontrado</td></tr>';
                }

                $('#cargos-edital > tbody').html($tr);
                if (data.edital[0].EdiExtratoLegislacao != "") {
                    $('#extrato-legislacao-edital').html('<div class="m-0">' + data.edital[0].EdiExtratoLegislacao + '</div>');
                } else {
                    $('#extrato-legislacao-edital').html('<div class="p-3 m-0 text-uppercase text-14 blue lighten-5 text-primary"><center><strong>O extrato e/ou legislação não foram cadastrados. Leia os arquivos do Edital.</strong></center></div>');
                }

                if (data.arquivos != null) {
                    $.each(data.arquivos, function (key, val) {
                        var arquivos = '<tr class="' + (val['destaque'] == 1 ? "warning" : "") + '"><td class="text-left" title="' + val['descricao'] + '">' + val['descricao'] + '</td><td class="text-center">' + val['data'] + ' - ' + val['hora'] + '<td class="text-center"><a href="'+$MIDIAS_URL+'edital/102/' + data.edital[0].EdiId + '/' + val['file'] + '" target="_blank"><i class="fe fe-download text-base text-18"></i></a></td></tr>';
                        $('#arquivos-edital > tbody').append(arquivos);
                    });
                } else {
                    var arquivos = '<tr class="red lighten-5"><td colspan="3" class="text-center py-3 text-danger" title="Nenhum arquivo foi encontrado">Nenhum arquivo foi encontrado</td></tr>';
                    $('#arquivos-edital > tbody').append(arquivos);


                }
                //
                // /* Linha do tempo */
                // var datainicio = data.cronograma.EdiInicioInscricoes.split(" - ");
                // var ano = datainicio[0].split("/");
                // var datafinal = data.cronograma.EndProHrDataInicio.split(" - ");
                // var anofinal = datafinal[0].split("/");
                //
                // var pagamento = data.cronograma.EdiDataLimiteBoleto.split('-');
                // pagamento = pagamento[0];
                //
                // var dataprova = data.cronograma.EndProHrDataInicio.split('-');
                // dataprova = dataprova[0];
                // var cronograma = '<ul class="timeline timeline_left text-14">' +
                //     '<li class="year"><span>' + ano[2] + '</span></li>' +
                //     '<li class="event"><div class="event__title">' +
                //     '<h3 class="text-400" title="Período de inscrições">Período de inscrições</h3>' +
                //     '<div class="text-secondary"><span class="status-icon bg-success"></span> ' + data.cronograma.EdiInicioInscricoes + '</div>' +
                //     '<div class="text-secondary"><span class="status-icon bg-danger"></span> ' + data.cronograma.EdiFimInscricoes + '</div>' +
                //     '</div></li>';
                // if(data.edital[0].EdiId == 1238){
                //     cronograma += '<li class="event"><div class="event__title">' +
                //         '<h3 class="text-400" title="Data limite de pagamentos">Data limite de pagamentos</h3>' +
                //         '<div class="text-secondary"><span class="status-icon bg-danger"></span> 24/10/2017</div>' +
                //         '</div></li>';
                // }else {
                //     if (data.cronograma.EdiFormaPagamento != 0) {
                //         cronograma += '<li class="event"><div class="event__title">' +
                //             '<h3 class="text-400" title="Data limite de pagamentos">Data limite de pagamentos</h3>' +
                //             '<div class="text-secondary"><span class="status-icon bg-danger"></span> ' + pagamento + '</div>' +
                //             '</div></li>';
                //     }
                // }
                // cronograma += '<li class="event"><div class="event__title">' +
                //     '<h3 class="text-400" title="Data de homologação">Data de homologação das inscrições</h3>' +
                //     '<div class="text-secondary"><span class="status-icon bg-danger"></span> ' + data.cronograma.EdiHomologacao + '</div>' +
                //     '</div></li>';
                // if(data.edital[0].EndProvaDoisPeriodos == 1) {
                //     cronograma += '<li class="event"><div class="event__title">' +
                //         '<h3 class="text-400 text-15" title="Data da Prova Objetiva">Data provável da Prova Teórico-Objetiva</h3>' +
                //         '<div class="text-secondary"><span class="status-icon bg-danger"></span> ' + dataprova + '</div>' +
                //         '</div></li>';
                // }
                // if (data.cronograma.recursos != null) {
                //     cronograma += '<li class="event"><div class="event__title"><h3 class="text-400" title="Recursos">Recursos</h3></div>';
                //     $.each(data.cronograma.recursos, function(key, val) {
                //         cronograma += ' <div class="event__content bg-light border-right-0 border-left-0"><p class="text-dark" title="' + val['nome'] + '">' + val['nome'] + '</p>' +
                //             '<time class="text-secondary"><span class="status-icon bg-success"></span> ' + val['dataInicio'] + '</time><br>' +
                //             '<time class="text-secondary"><span class="status-icon bg-danger"></span> ' + val['dataFim'] + '</time></div>';
                //     });
                //     cronograma += '</li>';
                // }
                // cronograma += '<li class="clearfix"></li><li class="year"><span class="mb-0">' + anofinal[2] + '</span></li>';
                // $('#calendar').html(cronograma);

                $('#visualizar-edital').removeClass('d-none')
            }
        }).done(function(){
            $('.header-loader').addClass('d-none');
        });
    }

    function getFilterEditais(status, cid_id) {
        $.getJSON($WS_URL+"editais/" + status + "/" + cid_id, function(data) {
            $('#editais_lista span').remove();
            if (data['editais'] == null) {
                $('#editais_lista').html('<div class="col-sm-12">' +
                    '<div class="py-4">\n' +
                    '                            <div class="row">\n' +
                    '                                <div class="col"></div>\n' +
                    '                                <div class="col-md-6 text-center text-base rounded">\n' +
                    '                                    <h1 class="text-400"><i class="fe fe-alert-circle"></i></h1>\n' +
                    '                                    <p class="text-700 text-16">NENHUM CONCURSO OU PROCESSO SELETIVO ENCONTRADO PARA ESTA CIDADE</p>\n' +
                    '                                </div>\n' +
                    '                                <div class="col"></div>\n' +
                    '                            </div>\n' +
                    '                        </div>' +
                    '</div>');
            } else {
                var tabindex = 13;
                $('#filtro').html(data.editais[0].CidNome + ' - ' + data.editais[0].EstSigla);
                if (status == 1) {
                    $("#status_editais").html('Futuros');
                } else if (status == 2) {
                    $("#status_editais").html('Inscrições abertas');
                } else if (status == 3) {
                    $("#status_editais").html('Inscrições finalizadas');
                } else if (status == 4) {
                    $("#status_editais").html('Encerrados');
                }

                var $link = '';
                var $edital = '<div class="list-group list-group-flush mt-0">';

                $.each(data.editais, function(key, val) {
                    var p_edital_inscricoes = "";

                    var $inicio = val['EdiInicioInscricoes'].split(" ");
                    var $final = val['EdiFimInscricoes'].split(" ");

                    if (val['EdiStatus']=='2') {
                        $link = '<div class="col-lg-3 col-md-3 text-center text-12 text-500 yellow lighten-5 py-5 h-100">\n' +
                            '            <div class="w-100">\n' +
                            '                 <b class="text-13">PERÍODO DE INSCRIÇÕES</b><br>\n' +
                            '                 <b class="text-muted">INÍCIO:</b> '+$inicio[0]+' '+$inicio[1]+'<br>\n' +
                            '                 <b class="text-muted">TÉRMINO:</b> '+$final[0]+' '+$final[1]+'<br>\n' +
                            '                 <a class="btn btn-yellow text-700 mt-2" href="'+$BASE_URL+'editais/ver/'+val['EdiLink']+'">INSCREVA-SE</a>\n' +
                            '             </div>\n' +
                            '         </div>';
                    } else if (val['EdiStatus']=='3') {
                        $link = '<div class="col-lg-3 col-md-3 text-center text-12 text-500 yellow lighten-5 py-5 h-100">\n' +
                            '            <div class="w-100">\n' +
                            '                 <b class="text-13">PERÍODO DE INSCRIÇÕES</b><br>\n' +
                            '                 <b class="text-muted">INÍCIO:</b> '+$inicio[0]+' '+$inicio[1]+'<br>\n' +
                            '                 <b class="text-muted">TÉRMINO:</b> '+$final[0]+' '+$final[1]+'<br>\n' +
                            '                 <a class="btn btn-yellow btn-sm disabled text-500 mt-2" href="javascript:void(0)">FORA DO PERÍODO</a>\n' +
                            '             </div>\n' +
                            '         </div>';
                    } else if (val['EdiStatus']=='4') {
                        $link = '<div class="col-lg-3 col-md-3 text-center text-12 text-500 yellow lighten-5 py-5 h-100">\n' +
                            '            <div class="w-100">\n' +
                            '                 <b class="text-13">PERÍODO DE INSCRIÇÕES</b><br>\n' +
                            '                 <b class="text-muted">INÍCIO:</b> '+$inicio[0]+' '+$inicio[1]+'<br>\n' +
                            '                 <b class="text-muted">TÉRMINO:</b> '+$final[0]+' '+$final[1]+'<br>\n' +
                            '                 <a class="btn btn-danger btn-sm disabled text-500 mt-2" href="javascript:void(0)">EDITAL ENCERRADO</a>\n' +
                            '             </div>\n' +
                            '         </div>';
                    } else if (val['EdiStatus']=='1') {
                        $link = '<div class="col-lg-3 col-md-3 text-center text-12 text-500 yellow lighten-5 py-5 h-100">\n' +
                            '            <div class="w-100">\n' +
                            '                 <b class="text-13">PERÍODO DE INSCRIÇÕES</b><br>\n' +
                            '                 <b class="text-muted">INÍCIO:</b> Previsto<br>\n' +
                            '                 <b class="text-muted">TÉRMINO:</b> Previsto<br>\n' +
                            '                 <a class="btn btn-yellow btn-sm disabled text-500 mt-2" href="javascript:void(0)">AGUARDANDO INÍCIO</a>\n' +
                            '             </div>\n' +
                            '         </div>';
                    }

                    $edital += ' <div class="list-group-item border-0 pt-0 pb-4">\n' +
                        '                    <div class="row no-gutters align-items-center grey lighten-4">\n' +
                        '                        <div class="col-lg-3 col-md-12 text-center my-2 my-md-0">\n' +
                        '                            <img src="'+$MIDIAS_URL+'entidade/' + val['EntLogo'] + '" class="img-responsive mx-auto mt-4" style="max-width:150px; max-height: 60px; border-radius: 5px;">\n' +
                        '                            <p class="m-0 text-12 px-2">\n' +
                        '                                <span class="text-14 text-700">' + val['TipNome'] + ' <small>' + val['EdiNumero'] + '</small></span><br>\n' +
                        '                                ' + val['EntNome'] + '\n' +
                        '                            </p>\n' +
                        '                        </div>\n' +
                        '                        <div class="col-lg-2 col-md-3 text-center pt-2">\n' +
                        '                            <a href="javascript:void(0)" data-id="' + val['EdiLink'] + '" class="btn btn-outline-base btn-ver-edital border-secondary btn-sm w-75 text-10 text-500 py-3">\n' +
                        '                                VER<br>EDITAL<br>\n' +
                        '                                <i class="fa fa-file-alt fa-3x mt-3"></i>\n' +
                        '                            </a>\n' +
                        '                        </div>\n' +
                        '                        <div class="col-lg-2 col-md-3 text-center pt-2">\n' +
                        '                            <a href="javascript:void(0)" data-id="' + val['EdiLink'] + '" class="btn btn-outline-base border-secondary btn-ver-material-estudo btn-sm w-75 text-10 text-500 py-3">\n' +
                        '                                MATERIAL<br>DE ESTUDO<br>\n' +
                        '                                <i class="fa fa-copy fa-3x mt-3"></i>\n' +
                        '                            </a>\n' +
                        '                        </div>\n' +
                        '                        <div class="col-lg-2 col-md-3 text-center pt-2">\n' +
                        '                            <a href="'+$BASE_URL+'editais/ver/'+val['EdiLink']+'" class="btn btn-outline-base border-secondary btn-sm w-75 text-10 text-500 py-3">\n' +
                        '                                MAIS<br>DETALHES<br>\n' +
                        '                                <i class="fa fa-plus-square fa-3x mt-3"></i>\n' +
                        '                            </a>\n' +
                        '                        </div>\n' + $link +
                        '                    </div>\n' +
                        '                </div>';

                    tabindex +=1;
                });
                $('#editais_lista').html($edital+'</div>');
            }
        });
    }

    $(document).on("click", ".ver-edital", function(e) {
        e.preventDefault();
        var $this = $(this);
        window.location.href = $BASE_URL+'editais/ver/' + $this.attr('id');
    });

    if ($('#ver-edital').length > 0) {
        var edital = $('#edital').val();
        var prestador = $('#prestador').val();
        getEdital(edital, prestador);
    }

    if ($('#filter-editais').length > 0) {
        var cid_id = $('#cid_id').val();
        var status = $('#status').val();
        var prestador = $('#prestador').val();
        getFilterEditais(status, cid_id);
    }

    $(document).on('click','.btn-ver-edital',function(event){
        event.preventDefault();
        var $this = $(this);
        var $list = '';
        $.getJSON(($WS_URL+"editais/getArquivo/"+$this.attr('data-id')+"/1"), function(response){
            if(response.status===true) {

                var $count = response['arquivo'].length;

                $list += '<div class="">';
                $.each(response['arquivo'], function (i, item) {
                    $list += '<div class="media border-bottom border-yellow bg-light p-3 mb-2 rounded align-items-center">\n' +
                        '  <div class="media-body text-left">\n' +
                        '    <p class="mb-0 text-13 text-500 text-dark">'+item['UplDescricao']+'</p>\n' +
                        '  </div>\n' +
                        '  <a class="ml-3 text-12 text-700 btn btn-sm btn-outline-yellow" href="'+$MIDIAS_URL+'edital/102/' + item['edital_EdiId'] + '/' + item['UplNome'] + '" target="_blank">BAIXAR <i class="fe fe-download"></i></a>\n'+
                        ' </div>';
                });
                $list += '</div>';
                swal({
                    title: '<h5 class="text-500 text-dark mb-3">'+($count>1?'EDITAIS':'EDITAL')+' DE ABERTURA</h5>',
                    html: $list,
                    showCloseButton: true,
                    confirmButtonText: 'FECHAR',
                    confirmButtonClass: 'py-3 px-5'
                });
            }else{
                swal({
                    title: 'Atenção!',
                    type: 'notice',
                    html: '<p class="text-base text-16 text-500 mb-0">Arquivo de edital não cadastrado.</p>',
                    showCloseButton: true,
                });
            }
        });
    });

    $(document).on('click','.btn-ver-material-estudo',function(event){
        event.preventDefault();
        var $this = $(this);
        var $list = '';
        $.getJSON(($WS_URL+"editais/getArquivo/"+$this.attr('data-id')+"/20"), function(response){
            if(response['status']===true) {
                $list += '<div class="">';
                $.each(response['arquivo'], function (i, item) {
                    $list += '<div class="media border-bottom border-yellow bg-light p-3 mb-2 rounded align-items-center">\n' +
                        '  <div class="media-body text-left">\n' +
                        '    <p class="mb-0 text-13 text-500 text-dark">'+item['UplDescricao']+'</p>\n' +
                        '  </div>\n' +
                        '  <a class="ml-3 text-12 text-700 btn btn-sm btn-outline-yellow" href="'+$MIDIAS_URL+'edital/102/' + item['edital_EdiId'] + '/' + item['UplNome'] + '" target="_blank">BAIXAR <i class="fe fe-download"></i></a>\n'+
                        ' </div>';
                });
                $list += '</div>';
                swal({
                    title: '<h5 class="text-500 text-dark mb-3">LEGISLAÇÃO</h5>',
                    html: $list,
                    showCloseButton: true,
                    confirmButtonText: 'FECHAR',
                    confirmButtonClass: 'py-3 px-5'
                });
            }else{
                swal({
                    title: 'LEGISLAÇÃO',
                    type: 'notice',
                    html: '<p class="text-base text-16 text-500 mb-0">A legislação poderá ser encontrada no site da Prefeitura e/ou da Câmara Municipal.</p>',
                    showCloseButton: true,
                });
            }

        });
    });
});

