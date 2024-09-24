import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from tkcalendar import DateEntry

def conectar_db():
    conn = sqlite3.connect("dizimos.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS fieis (
                    id INTEGER PRIMARY KEY,
                    nome TEXT,
                    salario REAL,
                    endereco TEXT,
                    cargo TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS dizimos (
                    id INTEGER PRIMARY KEY,
                    fiel_id INTEGER,
                    dizimo REAL,
                    pago BOOLEAN,
                    data TEXT,
                    FOREIGN KEY (fiel_id) REFERENCES fieis (id))''')
    conn.commit()
    return conn

def cadastrar_fiel():
    nome = entry_nome.get()
    salario = float(entry_salario.get())
    endereco = entry_endereco.get()
    cargo = entry_cargo.get()

    conn = conectar_db()
    c = conn.cursor()
    c.execute("INSERT INTO fieis (nome, salario, endereco, cargo) VALUES (?, ?, ?, ?)", 
              (nome, salario, endereco, cargo))
    conn.commit()
    conn.close()

    messagebox.showinfo("Cadastro", "Fiel cadastrado com sucesso!")
    
    entry_nome.delete(0, tk.END)
    entry_salario.delete(0, tk.END)
    entry_endereco.delete(0, tk.END)
    entry_cargo.delete(0, tk.END)

    atualizar_tabela_fieis()  

def calcular_dizimo(salario):
    return salario * 0.10

def registrar_pagamento():
    selected_item = tree_fieis.selection()
    if not selected_item:
        messagebox.showwarning("Seleção", "Por favor, selecione um fiel.")
        return

    fiel_id = tree_fieis.item(selected_item, 'values')[0]
    salario = float(tree_fieis.item(selected_item, 'values')[2]) 
    dizimo = calcular_dizimo(salario)
    data = date_entry.get()
    pago = var_pago.get()

    conn = conectar_db()
    c = conn.cursor()
    c.execute("INSERT INTO dizimos (fiel_id, dizimo, pago, data) VALUES (?, ?, ?, ?)", 
              (fiel_id, dizimo, pago, data))
    conn.commit()
    conn.close()

    messagebox.showinfo("Pagamento", f"Dízimo registrado com sucesso!\nValor do dízimo: R$ {dizimo:.2f}")
    var_pago.set(False) 

def atualizar_tabela_fieis():
    for row in tree_fieis.get_children():
        tree_fieis.delete(row)

    conn = conectar_db()
    c = conn.cursor()
    c.execute("SELECT * FROM fieis")
    for fiel in c.fetchall():
        tree_fieis.insert("", tk.END, values=fiel)

def exibir_pagamentos():
    for row in tree_pagamentos.get_children():
        tree_pagamentos.delete(row)

    conn = conectar_db()
    c = conn.cursor()
    c.execute("SELECT f.nome, d.dizimo, d.data FROM dizimos d JOIN fieis f ON d.fiel_id = f.id WHERE d.pago = 1")
    for pagamento in c.fetchall():
        tree_pagamentos.insert("", tk.END, values=pagamento)

root = tk.Tk()
root.title("Gerenciamento de Dízimos")
root.geometry("600x400")

tab_control = ttk.Notebook(root)

tab_cadastro = ttk.Frame(tab_control)
tab_control.add(tab_cadastro, text='Cadastro de Fiéis')

tk.Label(tab_cadastro, text="Nome:").grid(row=0, column=0, padx=10, pady=5, sticky='e')
entry_nome = tk.Entry(tab_cadastro, width=30)
entry_nome.grid(row=0, column=1, padx=10, pady=5)

tk.Label(tab_cadastro, text="Salário:").grid(row=1, column=0, padx=10, pady=5, sticky='e')
entry_salario = tk.Entry(tab_cadastro, width=30)
entry_salario.grid(row=1, column=1, padx=10, pady=5)

tk.Label(tab_cadastro, text="Endereço:").grid(row=2, column=0, padx=10, pady=5, sticky='e')
entry_endereco = tk.Entry(tab_cadastro, width=30)
entry_endereco.grid(row=2, column=1, padx=10, pady=5)

tk.Label(tab_cadastro, text="Cargo:").grid(row=3, column=0, padx=10, pady=5, sticky='e')
entry_cargo = tk.Entry(tab_cadastro, width=30)
entry_cargo.grid(row=3, column=1, padx=10, pady=5)

tk.Button(tab_cadastro, text="Cadastrar Fiel", command=cadastrar_fiel).grid(row=4, columnspan=2, pady=10)

tab_pagamento = ttk.Frame(tab_control)
tab_control.add(tab_pagamento, text='Pagamento de Dízimos')

tk.Label(tab_pagamento, text="Selecione um Fiel:").grid(row=0, column=0, padx=10, pady=5)

tree_fieis = ttk.Treeview(tab_pagamento, columns=("ID", "Nome", "Salário"), show='headings')
tree_fieis.heading("ID", text="ID")
tree_fieis.heading("Nome", text="Nome")
tree_fieis.heading("Salário", text="Salário")
tree_fieis.grid(row=1, column=0, columnspan=2, padx=10, pady=5)

date_entry = DateEntry(tab_pagamento, width=27, background='darkblue', foreground='white', borderwidth=2)
date_entry.grid(row=2, column=0, padx=10, pady=5)

var_pago = tk.BooleanVar()
tk.Checkbutton(tab_pagamento, text="Foi pago?", variable=var_pago).grid(row=2, column=1, pady=5)

tk.Button(tab_pagamento, text="Registrar Pagamento", command=registrar_pagamento).grid(row=3, columnspan=2, pady=10)

def on_tab_selected(event):
    atualizar_tabela_fieis()

tab_control.bind("<<NotebookTabChanged>>", on_tab_selected)

tab_visualizacao = ttk.Frame(tab_control)
tab_control.add(tab_visualizacao, text='Visualização de Pagamentos')

tree_pagamentos = ttk.Treeview(tab_visualizacao, columns=("Nome", "Dízimo", "Data"), show='headings')
tree_pagamentos.heading("Nome", text="Nome")
tree_pagamentos.heading("Dízimo", text="Dízimo")
tree_pagamentos.heading("Data", text="Data")
tree_pagamentos.grid(row=0, column=0, padx=10, pady=5)

tk.Button(tab_visualizacao, text="Exibir Pagamentos do Mês", command=exibir_pagamentos).grid(row=1, column=0, pady=10)

atualizar_tabela_fieis()

tab_control.pack(expand=1, fill="both")

root.mainloop()
