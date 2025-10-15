# 🧪 Guia Rápido de Testes

## 📋 Pré-requisitos
- Sistema inicializado: `python main.py`
- Banco de dados criado automaticamente
- Turmas A e B criadas automaticamente

---

## 🎯 Teste 1: Distribuir Alunos Existentes

**Objetivo:** Organizar alunos antigos nas turmas

### Passo a Passo:
1. **Login como Secretary**
   - Usuário: (verifique no banco)
   - Senha: `pass123`

2. **Acessar Distribuição**
   - Clique em "🔄 Distribuir Alunos" no menu lateral

3. **Verificar Informações**
   - Veja quantos alunos estão sem turma
   - Observe a lista de alunos não distribuídos

4. **Distribuir Automaticamente**
   - Clique em "🔄 Distribuir Automaticamente"
   - Confirme a ação
   - Mensagem de sucesso deve aparecer

5. **Verificar Resultado**
   - Clique em "👥 Gerenciar Turmas"
   - Veja alunos distribuídos em Turma A e Turma B

**✅ Resultado Esperado:**
- Alunos divididos igualmente entre as turmas
- Nenhum aluno sem turma

---

## 🎯 Teste 2: Registrar Novo Estudante com Turma

**Objetivo:** Criar estudante já associado a uma turma

### Passo a Passo:
1. **Login como Secretary** (se não estiver logado)

2. **Registrar Estudante**
   - Clique em "📝 Registrar Estudante"

3. **Preencher Formulário**
   ```
   Primeiro Nome: Pedro
   Último Nome: Lima
   Username: pedro.lima
   Senha: pass123
   Email: pedro@email.com
   ```

4. **Selecionar Turma**
   - Marque "Turma A" (ou Turma B)

5. **Opcional: Matricular em Disciplinas**
   - Marque algumas disciplinas

6. **Enviar Registro**
   - Clique em "Enviar Registro"

**✅ Resultado Esperado:**
- Mensagem: "Estudante registrado com sucesso!"
- Mostra: Nome, Username, **Turma**, ID

---

## 🎯 Teste 3: Enviar Aviso para Turma Específica

**Objetivo:** Comunicar com uma turma específica

### Passo a Passo:
1. **Ainda como Secretary**
   - Clique em "📢 Enviar Avisos"

2. **Criar Aviso**
   ```
   Título: Prova de Matemática
   Conteúdo: A prova será na próxima sexta-feira às 14h. 
             Estudem os capítulos 1 a 5.
   Enviar para: Turma A
   Prioridade: Alta
   ```

3. **Enviar Aviso**
   - Clique em "📢 Enviar Aviso"

4. **Verificar Histórico**
   - Veja o aviso na seção "Avisos Recentes"
   - Indicador 🔴 para alta prioridade

**✅ Resultado Esperado:**
- Mensagem: "Aviso enviado para Turma A!"
- Aviso aparece no histórico

---

## 🎯 Teste 4: Visualizar Notificações como Estudante

**Objetivo:** Estudante ver avisos da sua turma

### Passo a Passo:
1. **Logout** (clique em "⎋ Sair")

2. **Login como Estudante da Turma A**
   - Usuário: `student1` (ou qualquer da Turma A)
   - Senha: `pass123`

3. **Acessar Notificações**
   - Clique na aba "🔔 Notificações"

4. **Verificar Conteúdo**
   - Veja sua turma no topo (ex: "Turma A")
   - Veja o aviso "Prova de Matemática" 🔴
   - Indicador de alta prioridade em vermelho

5. **Testar com Turma B**
   - Logout
   - Login como estudante da Turma B
   - Na aba Notificações: NÃO deve ver aviso da Turma A
   - Deve ver apenas avisos gerais

**✅ Resultado Esperado:**
- Turma A vê aviso de alta prioridade
- Turma B NÃO vê aviso direcionado à Turma A
- Ambas veem avisos gerais (target_class_id = NULL)

---

## 🎯 Teste 5: Filtrar Alunos por Turma (Professor)

**Objetivo:** Professor visualizar alunos de uma turma específica

### Passo a Passo:
1. **Logout e Login como Professor**
   - Usuário: `teacher1`
   - Senha: `pass123`

2. **Selecionar Disciplina**
   - Escolha uma disciplina no dropdown

3. **Visualizar Todos**
   - Dropdown "Filtrar por Turma" deve estar em "Todas"
   - Veja todos os alunos com suas turmas na coluna

4. **Filtrar Turma A**
   - Selecione "Turma A" no filtro
   - Tabela atualiza automaticamente
   - Veja apenas alunos da Turma A

5. **Filtrar Turma B**
   - Selecione "Turma B"
   - Veja apenas alunos da Turma B

6. **Filtrar Sem Turma**
   - Selecione "Sem Turma"
   - Veja alunos não atribuídos (se houver)

7. **Mostrar Todos os Estudantes**
   - Clique em "Mostrar Todos os Estudantes"
   - Veja coluna "Turma" preenchida
   - Última coluna mostra disciplinas matriculadas

**✅ Resultado Esperado:**
- Filtro funciona corretamente
- Coluna "Turma" sempre visível
- Valores: "Turma A", "Turma B", ou "Sem Turma"

---

## 🎯 Teste 6: Distribuição Manual de Alunos

**Objetivo:** Mover alunos específicos para turmas

### Passo a Passo:
1. **Login como Secretary**

2. **Criar Novo Estudante SEM Turma**
   - Registre normalmente (Teste 2)
   - Mas remova-o da turma depois (ou use função de remoção)

3. **Acessar Distribuição**
   - "🔄 Distribuir Alunos"

4. **Seleção Manual**
   - Selecione 2-3 alunos da lista (Ctrl+Click)
   - Clique "➡️ Mover para Turma A"

5. **Verificar**
   - Alunos selecionados devem sumir da lista
   - Ir em "👥 Gerenciar Turmas"
   - Ver alunos na Turma A

**✅ Resultado Esperado:**
- Alunos movidos aparecem na turma correta
- Lista de "sem turma" atualiza

---

## 🔍 Checklist de Verificação

### Interface do Estudante
- [ ] Aba "📚 Minhas Disciplinas" funciona
- [ ] Aba "🔔 Notificações" existe
- [ ] Nome da turma aparece
- [ ] Avisos da turma aparecem
- [ ] Avisos gerais aparecem
- [ ] Indicadores 🟢/🔴 funcionam
- [ ] Sem turma mostra alerta laranja

### Interface da Secretária
- [ ] Formulário tem seleção de turma
- [ ] Turma é obrigatória
- [ ] Confirmação mostra turma
- [ ] Menu "Distribuir Alunos" existe
- [ ] Botão "Distribuir Automaticamente" funciona
- [ ] Botões "Turma A/B" funcionam
- [ ] Estatísticas aparecem
- [ ] Envio de avisos funciona

### Interface do Professor
- [ ] Dropdown "Filtrar por Turma" existe
- [ ] Opções: Todas, Turma A, Turma B, Sem Turma
- [ ] Filtro atualiza tabela
- [ ] Coluna "Turma" visível
- [ ] Valores corretos na coluna
- [ ] "Mostrar Todos" inclui turma

---

## 🐛 Problemas Comuns e Soluções

### 1. "Nenhum aluno sem turma"
**Causa:** Todos já foram distribuídos
**Solução:** Criar novo estudante ou remover um da turma

### 2. "Estudante não vê notificações"
**Causa:** Não está em nenhuma turma
**Solução:** Secretária deve distribuir o aluno

### 3. "Coluna Turma vazia"
**Causa:** Banco não atualizado
**Solução:** Reiniciar aplicação (cria tabelas automaticamente)

### 4. "Filtro não funciona"
**Causa:** Disciplina não selecionada
**Solução:** Selecionar disciplina primeiro

---

## 📊 Dados de Teste Sugeridos

### Estudantes para Criar
```
1. Nome: Ana Costa      | Turma: A
2. Nome: Bruno Souza    | Turma: A
3. Nome: Carla Lima     | Turma: B
4. Nome: Diego Santos   | Turma: B
```

### Avisos para Enviar
```
1. Título: "Boas Vindas"
   Destino: Todas as Turmas
   Prioridade: Normal

2. Título: "Reunião - Turma A"
   Destino: Turma A
   Prioridade: Alta

3. Título: "Atividade Extra - Turma B"
   Destino: Turma B
   Prioridade: Normal
```

---

## ✅ Teste Completo - 10 Minutos

**Ordem recomendada:**
1. ✅ Teste 1: Distribuir alunos (2 min)
2. ✅ Teste 2: Registrar com turma (2 min)
3. ✅ Teste 3: Enviar aviso (1 min)
4. ✅ Teste 4: Ver notificações (2 min)
5. ✅ Teste 5: Filtrar turmas (2 min)
6. ✅ Teste 6: Distribuição manual (1 min)

**Total:** ~10 minutos para testar todas as funcionalidades!

---

**🎓 Sistema pronto para demonstração!**
