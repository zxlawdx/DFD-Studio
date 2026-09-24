"""Modelo reconstruído dos anexos; alterações propostas explicitadas nas notas."""
import model

def build():
    d=model.blank()
    d['title']='Módulo 01 — Recebimento de parcelas'
    d['notes']=('Revisão da atividade 06: acrescentadas as conexões 1.8 → 1.11 e 1.13 → 1.04. '
        'Processos 1.15 e 1.16 acrescentados para verificar antecipação e calcular desconto. '
        'Layout reorganizado a partir do material fornecido. O processo 1.04 aparece uma única vez.\n\n'
        'Proposta de regra: antecipação ocorre quando a data do pagamento é anterior ao vencimento. '
        'O percentual e a base de cálculo devem ser definidos nas Tabelas do sistema; o enunciado não informa valores. '
        'O fluxo de desconto chega ao registro do novo valor (1.8), antes do pagamento (1.11). '
        'Para pagamento na data, registrar o valor original; para atraso, aplicar o fluxo de juros e correção. '
        'DFD representa dados, não a ordem de execução nem decisões de um fluxograma. '
        'Validar as regras propostas com o professor.')
    def n(id,kind,code,text,x,y,**kw):
        d['nodes'].append(model.node(kind,code,text,x,y,id=id,**kw));return id
    def p(id,code,text,x,y,**kw):return n(id,'process',code,text,x,y,**kw)
    def s(id,code,text,x,y,**kw):return n(id,'store',code,text,x,y,w=220,h=62,**kw)
    def e(a,b,text='',**kw):d['edges'].append(model.edge(a,b,text,**kw))
    n('client','entity','','Cliente',60,170,w=190,h=85)
    p('p1','1.1','Obter informação do cliente',380,160)
    p('p2','1.2','Verificar existência do cliente',760,160)
    p('p3','1.3','Verificar existência de parcelas',1140,160)
    p('p7','1.7','Verificar data de vencimento',1520,160,details='Entradas: parcela e data prevista/efetiva de pagamento. Separar dados de parcelas em atraso, no vencimento e antecipadas. A comparação não substitui a confirmação do pagamento.')
    p('p5','1.5','Rejeitar solicitação',760,365)
    p('p6','1.6','Calcular dias de atraso',1140,560)
    p('p10','1.10','Calcular índice de correção',800,560)
    p('p9','1.9','Calcular juros',460,560)
    p('p8','1.8','Registrar novo valor da parcela',120,560,details='Receber valor corrigido por atraso OU valor líquido após desconto por antecipação. Atualizar o histórico da parcela e encaminhar identificação, valor original, desconto/acréscimos e valor final ao processo 1.11.')
    p('p15','1.15','Verificar antecipação da parcela',1520,560,color=model.GREEN,details='Comparar data de pagamento com data de vencimento. Se pagamento < vencimento, produzir dados de antecipação para 1.16. No vencimento: desconto zero e valor original. Em atraso: encaminhar ao tratamento de atraso já existente em 1.7 / 1.6.')
    p('p16','1.16','Calcular desconto por antecipação',1520,780,color=model.GREEN,details='Consultar regra cadastrada em D-02. Desconto = função da regra, valor base e dias antecipados. Valor líquido = valor base − desconto. Garantir 0 ≤ desconto ≤ valor base. Percentual não definido no enunciado. Sem regra válida, não inventar desconto; solicitar validação.')
    p('p11','1.11','Registrar pagamento',800,1000,details='Conexão solicitada 1.8 → 1.11: receber parcela atualizada e registrar o valor efetivamente pago, sem aplicar o desconto novamente. Persistir em D-05 e enviar os dados ao caixa.')
    p('p14','1.14','Registrar pagamento no caixa',460,1000)
    p('p13','1.13','Gerar status de parcela paga',120,1000,details='Após confirmação do pagamento, atualizar o status da parcela e enviá-lo ao processo 1.04 para emissão do comprovante. Atualizar também o histórico da parcela.')
    p('p12','1.12','Gerar status de compras',120,1210)
    p('p4','1.04','Gerar comprovante de pagamento',460,1210,details='Receber status da parcela paga de 1.13 e informações da compra. Comprovante proposto: cliente, parcela, vencimento, data do pagamento, valor original, desconto, acréscimos e valor efetivamente pago. Entregar ao cliente.')
    s('d3','D-03','Cadastro de cliente',745,20)
    s('d6a','D-06','Histórico de parcelas',1125,20)
    s('d6b','D-06','Histórico de parcelas',105,800)
    s('d2','D-02','Tabelas do sistema',785,790,details='Calendário, juros, índice de correção e política de desconto por antecipação. As ocorrências D-02 representam o mesmo depósito.')
    s('d2b','D-02','Tabelas do sistema',1505,365)
    s('d4','D-04','Cadastro de compras',105,1410)
    s('d1','D-01','Caixa',445,1410)
    s('d5','D-05','Histórico de pagamentos',1120,1018)
    e('client','p1','Detalhes da solicitação')
    e('p1','p2','Cadastro do cliente')
    e('d3','p2','Detalhes de cadastro',route='vertical',label_dx=80)
    e('p2','p3','Dados do cliente')
    e('d6a','p3','Detalhes de parcelas',route='vertical',label_dx=85)
    e('p3','p7','Parcela e vencimento')
    e('p2','p5','Cadastro inexistente',route='vertical',label_dx=80)
    e('p3','p5','Parcela inexistente',source_port='bottom',target_port='right',bends=[[1235,415]],label_dx=0)
    e('p5','client','Informação de rejeição',source_port='left',target_port='bottom',bends=[[155,415]],label_dx=0)
    e('p7','p6','Parcela em atraso',source_port='left',target_port='top',bends=[[1430,210],[1430,500],[1235,500]],label_dx=-80)
    e('p6','p10','Dias de atraso')
    e('p10','p9','Detalhes de correção')
    e('p9','p8','Juros e correção')
    e('p8','d6b','Novo valor da parcela',route='vertical',label_dx=85)
    e('d2','p9','Regras de juros',source_port='left',target_port='bottom',bends=[[555,821]],label_dy=-12)
    e('d2','p10','Índice de correção',route='vertical',label_dx=82)
    e('d2','p6','Calendário',source_port='right',target_port='bottom',bends=[[1235,821]],label_dy=-12)
    e('d2','p5','Regras de validação',source_port='left',target_port='bottom',bends=[[720,821],[720,490],[855,490]],label_dx=-5,label_dy=70)
    e('p7','p11','Pagamento no vencimento',source_port='right',target_port='bottom',bends=[[1790,210],[1790,1140],[895,1140]],label_dx=95,label_dy=65)
    e('p7','p15','Datas e valor da parcela',color=model.GREEN,source_port='right',target_port='right',bends=[[1750,210],[1750,610]],label_dx=75)
    e('p15','p16','Dados de antecipação',color=model.GREEN,route='vertical',label_dx=88)
    e('d2b','p16','Regra de desconto',color=model.GREEN,source_port='left',target_port='left',bends=[[1480,396],[1480,830]],label_dx=-74)
    e('p16','p8','Valor líquido e desconto',color=model.GREEN,source_port='bottom',target_port='left',bends=[[1615,925],[55,925],[55,610]],label_dy=-15,details='Proposta de integração: o valor descontado passa pelo registro da parcela antes do pagamento.')
    e('p8','p11','Parcela atualizada / valor a pagar',color=model.GREEN,source_port='top',target_port='top',bends=[[215,500],[370,500],[370,890],[1090,890],[1090,940],[895,940]],label_dy=-15,details='Conexão explicitamente solicitada no enunciado: 1.8 com 1.11.')
    e('p11','d5','Registro do pagamento')
    e('p11','p14','Pagamento confirmado')
    e('p14','p13','Pagamento no caixa')
    e('p14','d1','Novos dados do caixa',source_port='right',target_port='right',bends=[[720,1050],[720,1441]],label_dx=78)
    e('p13','d6b','Status da parcela',route='vertical',label_dx=78,label_dy=35)
    e('p13','p12','Status da parcela paga',route='vertical',label_dx=-80)
    e('p12','d4','Status de compras',route='vertical',label_dx=80)
    e('p12','p4','Informações de compras')
    e('p13','p4','Parcela paga / comprovante',color=model.GREEN,source_port='right',target_port='top',bends=[[350,1050],[350,1155],[555,1155]],label_dx=70,label_dy=4,details='Conexão explicitamente solicitada no enunciado: 1.13 com 1.04.')
    e('p4','client','Comprovante de pagamento',source_port='bottom',target_port='left',bends=[[555,1370],[15,1370],[15,212]],label_dx=-5,label_dy=0)
    model.validate(d)
    return d

if __name__=='__main__':
    from pathlib import Path
    import exporter
    dest=Path(__file__).parent
    d=build()
    model.write(dest/'modulo_01.dfd.json',d)
    exporter.save_html(dest/'modulo_01_para_entrega.html',d)
    exporter.save_svg(dest/'modulo_01.svg',d)
