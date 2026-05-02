import os
from pathlib import Path

def listar_arquivos():
    """
    Lista todos os arquivos e pastas do projeto de transparência
    """
    # Caminho específico do seu projeto
    pasta_raiz = Path(r"C:\Users\jonat\OneDrive\Área de Trabalho\Desenvolvimento\TCC\projeto-transparencia")
    
    print(f"\n{'='*80}")
    print(f"📁 ESTRUTURA DO PROJETO: {pasta_raiz.name}")
    print(f"📍 Local: {pasta_raiz}")
    print(f"{'='*80}\n")
    
    total_arquivos = 0
    total_pastas = 0
    tamanho_total = 0
    
    for root, dirs, files in os.walk(pasta_raiz):
        # Ignora pastas que não são relevantes
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__' and d != 'node_modules']
        
        nivel = root.replace(str(pasta_raiz), '').count(os.sep)
        indent = '  ' * nivel
        
        # Mostra a pasta atual
        nome_pasta = os.path.basename(root)
        if nivel == 0:
            print(f"{indent}📂 {pasta_raiz.name}/")
            total_pastas += 1
        else:
            print(f"{indent}📂 {nome_pasta}/")
            total_pastas += 1
        
        # Mostra os arquivos
        subindent = '  ' * (nivel + 1)
        for file in sorted(files):
            if not file.startswith('.'):
                caminho_completo = os.path.join(root, file)
                try:
                    tamanho = os.path.getsize(caminho_completo)
                    tamanho_total += tamanho
                    
                    # Formata o tamanho
                    if tamanho < 1024:
                        tamanho_str = f"{tamanho} B"
                    elif tamanho < 1024 * 1024:
                        tamanho_str = f"{tamanho/1024:.1f} KB"
                    else:
                        tamanho_str = f"{tamanho/(1024*1024):.1f} MB"
                    
                    # Destaca diferentes tipos de arquivo
                    if file.endswith('.py'):
                        print(f"{subindent}🐍 {file} ({tamanho_str})")
                    elif file.endswith(('.html', '.htm')):
                        print(f"{subindent}🌐 {file} ({tamanho_str})")
                    elif file.endswith(('.css')):
                        print(f"{subindent}🎨 {file} ({tamanho_str})")
                    elif file.endswith(('.js')):
                        print(f"{subindent}⚡ {file} ({tamanho_str})")
                    elif file.endswith(('.json')):
                        print(f"{subindent}📋 {file} ({tamanho_str})")
                    elif file.endswith(('.md', '.txt')):
                        print(f"{subindent}📝 {file} ({tamanho_str})")
                    elif file.endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg')):
                        print(f"{subindent}🖼️  {file} ({tamanho_str})")
                    else:
                        print(f"{subindent}📄 {file} ({tamanho_str})")
                    
                    total_arquivos += 1
                except:
                    print(f"{subindent}❌ {file} (erro ao ler)")
    
    # Resumo final
    print(f"\n{'='*80}")
    print(f"📊 RESUMO:")
    print(f"   📁 Total de pastas: {total_pastas}")
    print(f"   📄 Total de arquivos: {total_arquivos}")
    
    # Formata tamanho total
    if tamanho_total < 1024:
        tamanho_total_str = f"{tamanho_total} B"
    elif tamanho_total < 1024 * 1024:
        tamanho_total_str = f"{tamanho_total/1024:.1f} KB"
    else:
        tamanho_total_str = f"{tamanho_total/(1024*1024):.1f} MB"
    
    print(f"   💾 Tamanho total: {tamanho_total_str}")
    print(f"{'='*80}\n")
    
    return {
        "pasta": str(pasta_raiz),
        "total_pastas": total_pastas,
        "total_arquivos": total_arquivos,
        "tamanho_total": tamanho_total
    }

if __name__ == "__main__":
    try:
        resultado = listar_arquivos()
        print("✅ Listagem concluída com sucesso!")
        print("🚀 Agora posso ver toda a estrutura do seu projeto!")
    except Exception as e:
        print(f"\n❌ Erro ao listar arquivos: {e}")
        print("Verifique se o caminho está correto e se você tem permissão de acesso.")