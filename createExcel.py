
import pandas as pd
import os
from datetime import datetime



class excel:

    def __init__(self, path, type_file):
        self.data = pd.read_excel(path, header=None)
        self.data['Tarefao'] = '0'
        self.data['Tarefinha'] = '0'
        self.projectName = self.data.columns[1]
        self.type_file = type_file
        
        self.main()

    def createMetaData(self):
        self.metaData = self.data.iloc[0:7, 0:2].copy()
        self.metaData = self.metaData.T
        self.metaData.columns = self.metaData.iloc[0, :]
        self.metaData.index = [0, self.projectName]
        self.metaData.drop([0], inplace= True)
        

        colunas = list(self.data.iloc[8, 0:-2].values)
        colunas.append('Tarefao')
        colunas.append('Tarefinha')
        self.data.drop(range(0, 9), inplace=True)
        self.data.columns = colunas

    def selectTask(self, col_ref):
        ultimaTarefona = self.data.iloc[0, col_ref]
        for i in range(len(self.data)-1):
            if len(self.data.iloc[i, col_ref].split('.')) < len(self.data.iloc[i+1, col_ref].split('.')):
                ultimaTarefona = self.data.iloc[i, col_ref]
                self.data.iloc[i, 16] = ultimaTarefona
            else:
                self.data.iloc[i, 17] = ultimaTarefona

        countLines = len(self.data)-1
        if len(self.data.iloc[countLines, col_ref].split('.')) < len(self.data.iloc[countLines-1, col_ref].split('.')):
            self.data.iloc[countLines,
                           16] = self.data.iloc[countLines, col_ref]
        else:
            self.data.iloc[countLines, 17] = ultimaTarefona

    def createFiles(self):
        tarefao = ['Task number', 'Outline number', 'Name', 'Assigned to', 'Start','Finish', 'Duration', 'Depends on', '% complete', 'Bucket','Dependents (after)', 'Effort', 'Effort completed', 'Effort remaining','Milestone', 'Notes', 'Tarefao']
        tarefinha = ['Task number', 'Outline number', 'Name', 'Assigned to', 'Start','Finish', 'Duration', 'Depends on', '% complete', 'Bucket','Dependents (after)', 'Effort', 'Effort completed', 'Effort remaining','Milestone', 'Notes', 'Tarefinha']
        hoje = datetime.now().strftime("%d_%m_%Y")
        if not os.path.isdir(f'{hoje}'): os.mkdir(hoje)
        self.data[self.data['Tarefao'] != '0'][tarefao].to_csv(f'./{hoje}/tarefasMacro_{self.type_file}.csv', index=False)
        self.data[self.data['Tarefinha'] != '0'][tarefinha].to_csv(f'./{hoje}/tarefasDetalhe_{self.type_file}.csv', index=False)
        self.metaData.to_csv(f'./{hoje}/metaData_{self.type_file}.csv', index=False)

    def main(self):
        self.createMetaData()
        self.selectTask(1)
        self.createFiles()


