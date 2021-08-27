import numpy as np
from datetime import datetime, timedelta
import pandas as pd

from createExcel import excel

arquivo = input('Digite o nome do arquivo: ')
type_file = input('DIGITI O TIPO DO ARQUIVO: ')
excel(f'./dados/{arquivo}',type_file)

hoje = datetime.now().strftime("%d_%m_%Y")
data = pd.read_csv(f'./{hoje}/tarefasDetalhe.csv')

"""**Converte as data para o formato datetime usado na biblioteca pandas**"""

data['Start'] = pd.to_datetime(data['Start'], format='%Y-%m-%d %H:%M:%S')
data['Finish'] = pd.to_datetime(data['Finish'], format='%Y-%m-%d %H:%M:%S')

"""**Funcao usada para informar qual sprint uma data pertence**
  + A funcao possui três parametros:
    + value: data que deseja obter a sprint 
    + init_date: data na qual inicia a primeira sprint
    + sprint_size: numero de dias ate a proxima sprint
"""

def sprint_date(value, type_file):
    if type_file == 'dtc':
      init_date='2021/07/05'
    elif type_file == 'time':
      init_date='2021/06/07'
    elif type_file == 'did':
      init_date='2021/06/07'

    sprint_size=14
    sprint=1
    init_date = datetime.strptime(init_date, '%Y/%m/%d')
    value = datetime.strptime(value, '%Y-%m-%d') if type(value) != pd.Timestamp and pd.notnull(value) else value

    while init_date <= value:
        init_date = init_date + timedelta(sprint_size)
        sprint = sprint+1

    return sprint-1

data['Sprint_calc'] = data['Finish'].apply(sprint_date, args=(type_file,))





"""**Funcao usada retornar somente o numro de dias da coluna 'Duration'**
  + '10 days' ------> 10
  + '5 days'  ------> 5
"""

def correct_duration(x):
  x = str(x)
  size_x = len(x)
  if size_x >6 and size_x<8:
    return x[:2]
  elif size_x >5 and size_x < 7:
    return x[0]

data['Duration'] = data['Duration'].apply(correct_duration)

""" + *Se a Data final < data de hoje, a coluna target terá o valor 1*
 + *Se a Data final >= data de hoje, a coluna target terá o valor representado pela seguinte formula:*
  + ( [data de hoje] - [data de inicio] ) / [numero de dias da semana]
"""

data['target'] = -99

for linha in range(len(data)):
    dias_da_semana = 7
    data_hoje = datetime.now()
    if data.loc[linha, 'Finish']<data_hoje:
        data.loc[linha, 'target'] = 1
    else:
        data.loc[linha, 'target'] = (data_hoje - data.loc[linha, 'Start'])/dias_da_semana

"""*A coluna target_semanal e a coluna Duration dividido por 5*"""

data['target_semanal'] = data['Duration'].apply(lambda x: int(x)/5 if x != None else x)

"""**Filtro das tarefas**"""

tarefas_concluidas = data[(data['target']==1)&(data['% complete']==1)]

tarefas_atrasadas = data[(data['target']==1)&(data['% complete']!=1)]

tarefas_adiantadas = data[(data['target']!=1)&(data['% complete']!=0)]

"""**New Table**"""

sprints = data['Sprint_calc'].value_counts().to_frame()
sprints.columns = ['count_task']

count_task_concluded = tarefas_concluidas.groupby(by='Sprint_calc').sum()['% complete'].to_frame()
count_task_concluded.columns = ['task_concluded']

count_task_late = tarefas_atrasadas.groupby(by='Sprint_calc').sum()['% complete'].to_frame()
count_task_late.columns = ['task_late']

count_task_advanced = tarefas_adiantadas.groupby(by='Sprint_calc').sum()['% complete'].to_frame()
count_task_advanced.columns = ['task_advanced']

table_summary = sprints.join(count_task_concluded)\
.join(count_task_late)\
.join(count_task_advanced)\
.sort_index()

aux_vet = range(max(table_summary.index)+1)
table_summary = table_summary.join(pd.DataFrame({'aux':aux_vet}, index= aux_vet), how='outer').drop('aux', axis=1)

table_summary.fillna(0, inplace=True)
table_summary.drop(0, inplace=True)
table_summary.index.name = 'sprint'

for i in table_summary.index:
  if table_summary.loc[i,'task_late'] != 0:
    table_summary.loc[i,'diference'] = table_summary.loc[i,'count_task'] - (table_summary.loc[i,'task_concluded'] + table_summary.loc[i,'task_advanced'] + (1 - table_summary.loc[i,'task_late']))
    table_summary.loc[i,'yield'] = table_summary.loc[i,'task_concluded'] + table_summary.loc[i,'task_advanced'] + (1 - table_summary.loc[i,'task_late'])

  else:
    table_summary.loc[i,'diference'] = table_summary.loc[i,'count_task'] - (table_summary.loc[i,'task_concluded'] + table_summary.loc[i,'task_advanced'])
    table_summary.loc[i,'yield'] = table_summary.loc[i,'task_concluded'] + table_summary.loc[i,'task_advanced']

sum_task_concluded = table_summary['task_concluded'].sum()
sum_task_advanced = table_summary['task_advanced'].sum()
sum_task_late = table_summary['task_late'].sum()

count_task_late = len(table_summary[table_summary['task_late']!=0])
dif_task_late = count_task_late - sum_task_late

Task_balance = int( sum_task_concluded + sum_task_advanced + dif_task_late )

print(f"Temos {Task_balance} tarefas concluídas")

table_summary['task_concluded_cumsum'] = table_summary['count_task'].cumsum()


sprint_atual = sprint_date(datetime.now().strftime('%Y-%m-%d'), type_file)
cumsum_redimento_grafico = table_summary['yield'].cumsum().values[:sprint_atual]
cumsum_redimento_grafico[-1] = cumsum_redimento_grafico[-1] + sum(table_summary['yield'].values[sprint_atual:])

table_summary['yield_cumsum'] = np.append(cumsum_redimento_grafico, [np.nan for _ in range(len(table_summary)-len(cumsum_redimento_grafico))])
#table_summary['yield_cumsum'] = table_summary['yield'].cumsum()

table_summary.to_csv(f'./info/report_{type_file}.csv')

"""**Charts**"""

from matplotlib import pyplot as plt

fig, axe = plt.subplots(figsize=(15,15))

table_summary[['yield_cumsum', 'task_concluded_cumsum']].plot(kind='line',
                                                              xticks=range(len(table_summary)+1),
                                                              title='Burnup Chart',
                                                              xlabel='Sprint',
                                                              ylabel='Count',
                                                              ax = axe)#.get_figure().savefig('Burnup_Chart.jpg')

point_x = [sprint_atual,sprint_atual]
point_y = [\
            table_summary.loc[sprint_atual, 'yield_cumsum'],
            table_summary.loc[sprint_atual, 'task_concluded_cumsum']
          ]

color = ['blue', 'coral']
axe.scatter(point_x,point_y, label=['yield_cumsum', 'task_concluded_cumsum'], c=color)

axe.annotate(point_y[0], (point_x[0]+0.5, point_y[0]-0.5))
axe.annotate(point_y[1], (point_x[1], point_y[1]+1))

fig.savefig(f'./info/Burnup_Chart_{type_file}.jpg')