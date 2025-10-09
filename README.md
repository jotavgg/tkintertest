# Sistema de Colaboração Acadêmica - Protótipo Tkinter

## Visão Geral
Esta é uma aplicação desktop funcional para um Sistema de Colaboração Acadêmica construída usando a biblioteca Tkinter do Python. Ela demonstra a lógica de negócio central para um sistema de gerenciamento universitário com diferentes papéis de usuário e funcionalidades.

## Funcionalidades

### Sistema de Autenticação Multi-Papel
- **Dashboard do Professor**: Gerenciamento de disciplinas, inserção de notas, busca de estudantes, identificação de estudantes em risco
- **Dashboard do Estudante**: Visualizar disciplinas matriculadas, notas e prazos de atividades
- **Dashboard da Secretária**: Importação de dados Excel, integração com módulo C para registro de estudantes

### Funcionalidade Principal
1. **Integração com Banco de Dados SQLite**: Armazena usuários, disciplinas, matrículas, atividades e entregas
2. **Importação de Dados Excel**: Importar dados de estudantes de arquivos Excel usando pandas e openpyxl
3. **Integração com Módulo C**: Integração simulada com programas externos em C para gerenciamento de estudantes
4. **Funcionalidade IA**: Identifica estudantes em risco baseado em limites de nota

## Instalação & Configuração

### Pré-requisitos
- Python 3.7 ou superior
- Os seguintes pacotes são instalados automaticamente:
  - pandas
  - openpyxl
  - sqlite3 (built-in)
  - tkinter (built-in)

### Executando a Aplicação
1. Navegue até o diretório do projeto
2. Execute a aplicação:
   ```bash
   python main.py
   ```

## Credenciais de Login de Exemplo

| Papel | Username | Password |
|------|----------|----------|
| Professor | teacher1 | pass123 |
| Estudante | student1 | pass123 |
| Estudante | student2 | pass123 |
| Secretária | secretary1 | pass123 |

## Esquema do Banco de Dados

A aplicação cria automaticamente um banco de dados SQLite (`academic_system.db`) com as seguintes tabelas:

- **users**: Contas de usuário com papéis (TEACHER, STUDENT, SECRETARY)
- **courses**: Disciplinas acadêmicas vinculadas aos professores
- **enrollments**: Relacionamento muitos-para-muitos entre usuários e disciplinas
- **assignments**: Atividades das disciplinas
- **submissions**: Entregas dos estudantes com notas
- **quiz_questions**: Questões de quiz com múltipla escolha
- **quiz_answers**: Respostas dos estudantes aos quizzes

## Testando as Funcionalidades

### Importação Excel (Secretária)
1. Faça login como `secretary1`
2. Clique em "Importar Estudantes do Excel"
3. Selecione o arquivo `sample_students.xlsx` fornecido
4. O sistema importará os dados dos estudantes para o banco de dados

### Identificação de Estudantes em Risco (Professor)
1. Faça login como `teacher1`
2. Selecione uma disciplina no dropdown
3. Clique em "Ver Estudantes em Risco"
4. O sistema mostrará estudantes com média de notas abaixo de 6.0

### Integração com Módulo C (Secretária)
1. Faça login como `secretary1`
2. Clique em "Registrar Estudante (Módulo C)"
3. Preencha **todas as informações obrigatórias**: Primeiro Nome, Último Nome, Username, Password e Email
4. **Opcionalmente selecione disciplinas** para matricular o estudante usando os checkboxes
5. O sistema simula a chamada de um programa externo em C para registro
6. O novo estudante pode fazer login imediatamente com as credenciais fornecidas

### Gerenciamento de Lista de Estudantes (Professores/Secretárias)
1. **Professores**: 
   - Use o botão "Atualizar Estudantes" para atualizar a lista de estudantes após novos registros
   - Use "Mostrar Todos os Estudantes" para ver todos os estudantes independente da matrícula em disciplina
   - Selecione uma disciplina específica para ver apenas estudantes matriculados naquela disciplina
2. **Secretárias**: Use "Ver Todos os Estudantes" para ver uma lista completa de todos os estudantes registrados
3. **Secretárias**: Use "Gerenciar Registros de Estudantes" para gerenciamento básico de registros de estudantes

### Busca de Estudantes (Professores)
1. Faça login como professor
2. Clique em "Buscar Estudantes"
3. Digite parte do primeiro ou último nome de um estudante
4. Pressione Enter ou clique em "Buscar" para encontrar estudantes correspondentes
5. Os resultados mostram nomes de estudantes e endereços de email (senhas não são exibidas por segurança)

### Funções da Secretária (Totalmente Implementadas)
1. **Processar Matrículas**: 
   - Selecione um estudante e matricule-o em múltiplas disciplinas
   - Visualize matrículas atuais para cada estudante
   - Previne matrículas duplicadas
2. **Gerar Relatórios de Estudantes**:
   - Crie relatórios de matrícula, relatórios de desempenho acadêmico, listas de contato ou resumos completos
   - Exporte relatórios para arquivos CSV ou exiba na janela
   - Múltiplos formatos de relatório disponíveis

### Gerenciamento de Conteúdo da Disciplina (Professores)
1. **Criar Atividade**:
   - Crie atividades com título, descrição, prazo e valores de pontos
   - Selecione tipos de atividade (homework, quiz, project, exam)
   - Atividades são armazenadas no banco de dados
2. **Materiais da Disciplina**:
   - Gerencie ementa, aulas e recursos
   - Interface com abas para diferentes tipos de conteúdo
   - Adicione aulas personalizadas e materiais da disciplina
3. **Ver Entregas**:
   - Visualize entregas de estudantes para atividades
   - Avalie entregas com notas numéricas e feedback
   - Acompanhe status de entrega (entregue, faltando, avaliado)

### Sistema de Quiz (Professores e Estudantes)
1. **Criar Quiz (Professores)**:
   - Crie quizzes com múltiplas questões de múltipla escolha
   - Defina 4 opções de resposta (A, B, C, D) para cada questão
   - Especifique a resposta correta e pontuação
   - Interface com scroll para adicionar várias questões
2. **Responder Quiz (Estudantes)**:
   - Visualize questões do quiz de forma clara e organizada
   - Selecione respostas usando radio buttons
   - Receba nota automática ao submeter
   - Veja análise detalhada de acertos e erros

## Estrutura de Arquivos

```
tkintertest/
├── main.py                      # Arquivo principal da aplicação
├── academic_system.db           # Banco de dados SQLite (criado automaticamente)
├── sample_students.xlsx         # Arquivo Excel de exemplo para testes
├── sample_students.csv          # Formato CSV alternativo
├── update_course_names.py       # Script para atualizar nomes de disciplinas
├── github/
│   └── copilot-instructions.md  # Especificações do projeto
└── README.md                    # Este arquivo
```

## Correções e Melhorias Principais

### Atualizações Recentes (Problemas Corrigidos)
1. **Registro Completo de Estudante**: Registro do Módulo C agora coleta todos os campos obrigatórios (Primeiro Nome, Último Nome, Username, Password, Email)
2. **Matrícula em Disciplina Durante Registro**: Estudantes agora podem ser matriculados em disciplinas durante o processo de registro
3. **Atualização de Lista de Estudantes**: Professores agora podem atualizar listas de estudantes para ver estudantes recém-registrados
4. **Funcionalidade Mostrar Todos os Estudantes**: Professores podem ver todos os estudantes independente do status de matrícula
5. **Função de Busca Corrigida**: Busca de estudantes agora funciona corretamente e não expõe informações de senha
6. **Funções da Secretária Implementadas**: Todas as funções placeholder agora têm implementações completas
7. **Gerenciamento de Conteúdo da Disciplina**: Professores podem criar atividades, gerenciar materiais e avaliar entregas
8. **Sistema de Relatórios de Estudantes**: Gerar e exportar relatórios completos de estudantes
9. **Gerenciamento de Matrículas**: Processar matrículas de estudantes em disciplinas com validação
10. **Sistema de Quiz Completo**: Criação de quizzes com múltipla escolha, avaliação automática e análise de resultados
11. **Interface Aprimorada**: Melhorias em layouts de botões e design de janelas em toda a aplicação
12. **Tradução Completa para Português**: Toda a interface do usuário está em português brasileiro

## Detalhes de Implementação Principais

### Arquitetura Multi-Frame
- Usa uma abordagem de frame container onde diferentes "páginas" (frames) são empilhadas
- O método `App.show_frame()` alterna entre diferentes dashboards de papel de usuário
- Cada frame herda de `tk.Frame` e implementa sua própria interface

### Operações de Banco de Dados
- Todas as operações de banco de dados usam queries parametrizadas para prevenir SQL injection
- Conexão com banco de dados é aberta e fechada para cada operação
- Dados de exemplo são automaticamente inseridos na primeira execução

### Tratamento de Erros
- Blocos try-catch abrangentes para operações de banco de dados
- Mensagens de erro amigáveis ao usuário usando `messagebox`
- Validação de entrada para formulários e entrada de dados

## Especificações Técnicas

- **Framework GUI**: Python Tkinter (built-in)
- **Banco de Dados**: SQLite3 (built-in)
- **Processamento de Dados**: Pandas + OpenPyXL para manipulação de Excel
- **Integração Externa**: Módulo subprocess para simulação de programa C
- **Arquitetura**: Aplicação em arquivo único com design multi-frame

## Notas de Desenvolvimento

Este protótipo demonstra:
1. Autenticação completa de usuário e controle de acesso baseado em papel
2. Design e operações de banco de dados para gerenciamento acadêmico
3. Capacidades de importação/exportação de arquivos
4. Padrões de integração de sistema externo
5. Funcionalidades de IA/analytics para insights educacionais
6. Sistema completo de quiz com avaliação automática

A aplicação é projetada como uma prova de conceito funcional para um sistema de colaboração acadêmica maior baseado em web, mostrando a lógica de negócio central em um ambiente desktop.

## Solução de Problemas

### Problemas Comuns
1. **Erro de Importação**: Certifique-se de que pandas e openpyxl estão instalados
2. **Erro de Banco de Dados**: Delete `academic_system.db` para resetar o banco de dados
3. **Problemas de Importação Excel**: Certifique-se de que o arquivo Excel tem as colunas obrigatórias: username, first_name, last_name, email
4. **Disciplinas em Inglês**: Execute `python update_course_names.py` para atualizar os nomes das disciplinas no banco de dados

### Resetar Aplicação
Para resetar a aplicação completamente:
1. Delete `academic_system.db`
2. Reinicie a aplicação
3. Dados de exemplo novos serão criados automaticamente

### Atualizar Nomes de Disciplinas
Para atualizar os nomes das disciplinas para português:
```bash
python update_course_names.py
```

## Melhorias Futuras
- Compilação e integração real de módulo C
- Relatórios avançados com gráficos e charts
- Sistema de notificação por email
- Manipulação de submissão de atividades
- Funcionalidade de exportação de grade book
- Opções avançadas de busca e filtragem
- Mais tipos de questões para quizzes (verdadeiro/falso, dissertativas)
- Sistema de feedback em tempo real
