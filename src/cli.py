import sys
import click
from colorama import init, Fore, Style
import time
import os
from datetime import datetime
from .password_manager import PasswordManager

def clear_screen():
    """清除屏幕"""
    os.system('cls' if os.name == 'nt' else 'clear')

@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """Password Manager CLI Interface"""
    init(autoreset=True)  # 初始化colorama并自动重置颜色
    pm = PasswordManager()
    
    if ctx.invoked_subcommand is None:
        while True:
            clear_screen()
            click.echo(f"\n{Fore.CYAN}{pm.get_text('welcome')}{Style.RESET_ALL}")
            click.echo(pm.get_text('menu'))
            
            choice = click.prompt(f"\n{Fore.YELLOW}{pm.get_text('select_option')}{Style.RESET_ALL}")
            
            if choice == "1":
                clear_screen()
                click.echo(f"\n{Fore.CYAN}=== {pm.get_text('menu').split('\n')[1].strip()} ==={Style.RESET_ALL}")
                click.echo(f"\n{Fore.YELLOW}{pm.get_text('back_option')}{Style.RESET_ALL}")
                account = click.prompt(f"{Fore.GREEN}{pm.get_text('enter_account')}{Style.RESET_ALL}", type=str)
                if check_back(account):
                    click.echo(f"\n{Fore.YELLOW}{pm.get_text('going_back')}{Style.RESET_ALL}")
                    continue
                length = click.prompt(f"{Fore.GREEN}{pm.get_text('enter_password_length')}{Style.RESET_ALL}", type=str, default="12")
                if check_back(length):
                    click.echo(f"\n{Fore.YELLOW}{pm.get_text('going_back')}{Style.RESET_ALL}")
                    continue
                length = int(length) if length.isdigit() else 12
                exclude = click.prompt(f"{Fore.GREEN}{pm.get_text('enter_exclude_chars')}{Style.RESET_ALL}", type=str, default="")
                if check_back(exclude):
                    click.echo(f"\n{Fore.YELLOW}{pm.get_text('going_back')}{Style.RESET_ALL}")
                    continue
                note = click.prompt(f"{Fore.GREEN}{pm.get_text('enter_note')}{Style.RESET_ALL}", type=str, default="")
                if check_back(note):
                    click.echo(f"\n{Fore.YELLOW}{pm.get_text('going_back')}{Style.RESET_ALL}")
                    continue
                ctx.invoke(generate, length=length, exclude=exclude, account=account, note=note)
            
            elif choice == "2":
                clear_screen()
                click.echo(f"\n{Fore.CYAN}=== {pm.get_text('menu').split('\n')[2].strip()} ==={Style.RESET_ALL}")
                click.echo(f"\n{Fore.YELLOW}{pm.get_text('back_option')}{Style.RESET_ALL}")
                search = click.prompt(f"{Fore.GREEN}{pm.get_text('enter_search_keyword')}{Style.RESET_ALL}", type=str, default="")
                if check_back(search):
                    click.echo(f"\n{Fore.YELLOW}{pm.get_text('going_back')}{Style.RESET_ALL}")
                    continue
                ctx.invoke(list, search=search)
            
            elif choice == "3":
                clear_screen()
                click.echo(f"\n{Fore.CYAN}=== {pm.get_text('menu').split('\n')[3].strip()} ==={Style.RESET_ALL}")
                # 显示密码列表
                passwords = pm.get_passwords()
                if not passwords:
                    click.echo(f"\n{Fore.YELLOW}{pm.get_text('no_passwords')}{Style.RESET_ALL}")
                else:
                    click.echo(f"\n{Fore.GREEN}{pm.get_text('accounts_list')}{Style.RESET_ALL}")
                    for account in passwords:
                        click.echo(f"- {account['account']}")
            
            elif choice == "4":
                clear_screen()
                click.echo(f"\n{Fore.CYAN}=== {pm.get_text('menu').split('\n')[4].strip()} ==={Style.RESET_ALL}")
                
                # 先获取并显示前10条账户
                passwords = pm.get_passwords()
                if not passwords:
                    click.echo(f"\n{Fore.YELLOW}{pm.get_text('no_passwords')}{Style.RESET_ALL}")
                    continue
                
                # 默认显示前10条记录
                display_passwords = passwords[:10]
                total_count = len(passwords)
                
                click.echo(f"\n{Fore.GREEN}{pm.get_text('available_accounts')}{Style.RESET_ALL}")
                for p in display_passwords:
                    click.echo(f"{Fore.BLUE}{pm.get_text('account_id_format').format(p['id'], p['account'])}{Style.RESET_ALL}")
                
                # 如果总记录数超过10条，显示提示信息
                if total_count > 10:
                    click.echo(f"\n{Fore.YELLOW}{pm.get_text('more_records').format(total_count - 10)}{Style.RESET_ALL}")
                
                # 显示操作选项
                click.echo(f"\n{Fore.GREEN}{pm.get_text('delete_options')}{Style.RESET_ALL}")
                click.echo(f"{Fore.YELLOW}{pm.get_text('back_option')}{Style.RESET_ALL}")
                delete_choice = click.prompt(f"{Fore.GREEN}{pm.get_text('select_delete_option')}{Style.RESET_ALL}", type=str)
                
                if check_back(delete_choice):
                    click.echo(f"\n{Fore.YELLOW}{pm.get_text('going_back')}{Style.RESET_ALL}")
                    continue
                
                if delete_choice == "1":  # 直接输入ID删除
                    password_id = click.prompt(f"{Fore.GREEN}{pm.get_text('enter_password_id')}{Style.RESET_ALL}", type=str)
                    if check_back(password_id):
                        click.echo(f"\n{Fore.YELLOW}{pm.get_text('going_back')}{Style.RESET_ALL}")
                        continue
                    try:
                        password_id = int(password_id)
                        ctx.invoke(delete, password_id=password_id)
                    except ValueError:
                        click.echo(f"\n{Fore.RED}{pm.get_text('invalid_option')}{Style.RESET_ALL}")
                
                elif delete_choice == "2":  # 搜索后删除
                    search = click.prompt(f"{Fore.GREEN}{pm.get_text('search_before_delete')}{Style.RESET_ALL}", type=str)
                    if check_back(search):
                        click.echo(f"\n{Fore.YELLOW}{pm.get_text('going_back')}{Style.RESET_ALL}")
                        continue
                    
                    filtered_passwords = [p for p in passwords if search.lower() in p['account'].lower()]
                    if not filtered_passwords:
                        click.echo(f"\n{Fore.YELLOW}{pm.get_text('no_records_found')}{Style.RESET_ALL}")
                        continue
                    
                    display_passwords = filtered_passwords[:10]
                    total_count = len(filtered_passwords)
                    
                    click.echo(f"\n{Fore.GREEN}{pm.get_text('available_accounts')}{Style.RESET_ALL}")
                    for p in display_passwords:
                        click.echo(f"{Fore.BLUE}{pm.get_text('account_id_format').format(p['id'], p['account'])}{Style.RESET_ALL}")
                    
                    if total_count > 10:
                        click.echo(f"\n{Fore.YELLOW}{pm.get_text('more_records').format(total_count - 10)}{Style.RESET_ALL}")
                    
                    password_id = click.prompt(f"{Fore.GREEN}{pm.get_text('enter_password_id')}{Style.RESET_ALL}", type=str)
                    if check_back(password_id):
                        click.echo(f"\n{Fore.YELLOW}{pm.get_text('going_back')}{Style.RESET_ALL}")
                        continue
                    try:
                        password_id = int(password_id)
                        ctx.invoke(delete, password_id=password_id)
                    except ValueError:
                        click.echo(f"\n{Fore.RED}{pm.get_text('invalid_option')}{Style.RESET_ALL}")
                
                else:
                    click.echo(f"\n{Fore.RED}{pm.get_text('invalid_option')}{Style.RESET_ALL}")
            
            elif choice == "5":
                clear_screen()
                click.echo(f"\n{Fore.CYAN}=== {pm.get_text('menu').split('\n')[5].strip()} ==={Style.RESET_ALL}")
                click.echo(f"\n{Fore.YELLOW}{pm.get_text('back_option')}{Style.RESET_ALL}")
                export_path = click.prompt(f"{Fore.GREEN}{pm.get_text('enter_export_path')}{Style.RESET_ALL}", type=str)
                if check_back(export_path):
                    click.echo(f"\n{Fore.YELLOW}{pm.get_text('going_back')}{Style.RESET_ALL}")
                    continue
                ctx.invoke(export, path=export_path)
            
            elif choice == "6":
                clear_screen()
                click.echo(f"\n{Fore.CYAN}=== {pm.get_text('menu').split('\n')[6].strip()} ==={Style.RESET_ALL}")
                click.echo(f"\n{Fore.YELLOW}{pm.get_text('back_option')}{Style.RESET_ALL}")
                import_path = click.prompt(f"{Fore.GREEN}{pm.get_text('enter_import_path')}{Style.RESET_ALL}", type=str)
                if check_back(import_path):
                    click.echo(f"\n{Fore.YELLOW}{pm.get_text('going_back')}{Style.RESET_ALL}")
                    continue
                ctx.invoke(import_passwords, path=import_path)
            
            elif choice == "7":
                clear_screen()
                click.echo(f"\n{Fore.CYAN}=== {pm.get_text('menu').split('\n')[7].strip()} ==={Style.RESET_ALL}")
                click.echo(f"\n{Fore.YELLOW}{pm.get_text('back_option')}{Style.RESET_ALL}")
                lang = click.prompt(f"{Fore.GREEN}{pm.get_text('select_language')}{Style.RESET_ALL}", type=str)
                if check_back(lang):
                    click.echo(f"\n{Fore.YELLOW}{pm.get_text('going_back')}{Style.RESET_ALL}")
                    continue
                if not pm.set_language(lang):
                    click.echo(f"\n{Fore.RED}{pm.get_text('invalid_option')}{Style.RESET_ALL}")
                else:
                    click.echo(f"\n{Fore.GREEN}{pm.get_text('language_changed')}{Style.RESET_ALL}")
            
            elif choice == "8":
                clear_screen()
                click.echo(f"\n{Fore.YELLOW}{pm.get_text('goodbye')}{Style.RESET_ALL}")
                sys.exit(0)
            
            else:
                click.echo(f"\n{Fore.RED}{pm.get_text('invalid_option')}{Style.RESET_ALL}")
            
            if choice in ["1", "2", "3", "4", "5", "6", "7"]:
                click.prompt(f"\n{Fore.CYAN}{pm.get_text('press_enter')}{Style.RESET_ALL}", default="", show_default=False)

def get_help_text(key):
    """获取帮助文本"""
    pm = PasswordManager()
    return pm.get_text(key)

@cli.command()
@click.option('--length', '-l', default=12, help=get_help_text('help_password_length'))
@click.option('--exclude', '-e', default='', help=get_help_text('help_exclude_chars'))
@click.option('--account', '-a', required=True, help=get_help_text('help_account_name'))
@click.option('--note', '-n', default='', help=get_help_text('help_note'))
def generate(length, exclude, account, note):
    """Generate and save a new password"""
    pm = PasswordManager()
    
    while True:
        start_time = time.time()
        password = pm.generate_password(length, exclude)
        gen_time = time.time() - start_time
        
        click.echo(f"\n{Fore.YELLOW}{pm.get_text('generated_password')}{Style.RESET_ALL} {password}")
        generation_time_text = pm.get_text('generation_time').format(f"{gen_time:.3f}")
        click.echo(f"{Fore.CYAN}{generation_time_text}{Style.RESET_ALL}")
        
        if click.confirm(f"{Fore.GREEN}{pm.get_text('satisfied_password')}{Style.RESET_ALL}", default=True):
            start_time = time.time()
            pm.add_password(account, password, note)
            save_time = time.time() - start_time
            
            save_time_text = f"{save_time:.3f}{pm.get_text('seconds')}"
            click.echo(f"\n{Fore.GREEN}✓ {pm.get_text('password_saved')}{Style.RESET_ALL} ({save_time_text})")
            click.echo(f"{Fore.BLUE}{pm.get_text('enter_account').strip()}{Style.RESET_ALL} {account}")
            click.echo(f"{Fore.YELLOW}{pm.get_text('generated_password').strip()}{Style.RESET_ALL} {password}")
            if note:
                click.echo(f"{Fore.CYAN}{pm.get_text('enter_note').strip()}{Style.RESET_ALL} {note}")
            break
        else:
            if click.confirm(f"{Fore.YELLOW}{pm.get_text('modify_parameters')}{Style.RESET_ALL}", default=False):
                length = click.prompt(f"{Fore.GREEN}{pm.get_text('enter_new_length')}{Style.RESET_ALL}", type=int, default=length)
                exclude = click.prompt(f"{Fore.GREEN}{pm.get_text('enter_exclude_chars')}{Style.RESET_ALL}", type=str, default=exclude)
            click.echo(f"\n{Fore.CYAN}{pm.get_text('regenerating')}{Style.RESET_ALL}")

@cli.command()
@click.option('--search', '-s', help=get_help_text('help_search'))
def list(search):
    """List saved passwords"""
    pm = PasswordManager()
    
    start_time = time.time()
    passwords = pm.get_passwords(search)
    query_time = time.time() - start_time
    
    if not passwords:
        click.echo(f"\n{Fore.YELLOW}{pm.get_text('no_records_found')}{Style.RESET_ALL}")
        return
    
    query_time_text = f"{query_time:.3f}{pm.get_text('seconds')}"
    click.echo(f"\n{Fore.GREEN}{pm.get_text('found_records').format(len(passwords))}{Style.RESET_ALL} ({query_time_text})\n")
    
    for p in passwords:
        click.echo(f"{Fore.BLUE}ID{Style.RESET_ALL} {p['id']}")
        click.echo(f"{Fore.BLUE}账号{Style.RESET_ALL} {p['account']}")
        click.echo(f"{Fore.YELLOW}密码{Style.RESET_ALL} {p['password']}")
        if p['note']:
            click.echo(f"{Fore.CYAN}备注{Style.RESET_ALL} {p['note']}")
        click.echo(f"{Fore.MAGENTA}创建时间{Style.RESET_ALL} {p['created_at'].strftime('%Y-%m-%d %H:%M:%S')}")
        click.echo(f"{Fore.MAGENTA}更新时间{Style.RESET_ALL} {p['updated_at'].strftime('%Y-%m-%d %H:%M:%S')}")
        click.echo(f"{Fore.WHITE}{'-' * 50}{Style.RESET_ALL}")

@cli.command()
@click.argument('password_id', type=int)
def delete(password_id):
    """Delete a password"""
    pm = PasswordManager()
    
    # 先查询要删除的记录
    passwords = pm.get_passwords()
    target = next((p for p in passwords if p['id'] == password_id), None)
    
    if not target:
        click.echo(f"\n{Fore.RED}✗ {pm.get_text('account_not_found')}{Style.RESET_ALL}")
        return
    
    # 显示要删除的记录详情
    click.echo(f"\n{Fore.YELLOW}{pm.get_text('record_details')}{Style.RESET_ALL}")
    click.echo(f"{Fore.BLUE}ID{Style.RESET_ALL} {target['id']}")
    click.echo(f"{Fore.BLUE}账号{Style.RESET_ALL} {target['account']}")
    if target['note']:
        click.echo(f"{Fore.CYAN}备注{Style.RESET_ALL} {target['note']}")
    
    # 确认删除
    if not click.confirm(f"\n{Fore.RED}{pm.get_text('confirm_delete')}{Style.RESET_ALL}", default=False):
        click.echo(f"\n{Fore.YELLOW}{pm.get_text('delete_cancelled')}{Style.RESET_ALL}")
        return
    
    start_time = time.time()
    success = pm.delete_password(password_id)
    delete_time = time.time() - start_time
    
    if success:
        delete_time_text = f"{delete_time:.3f}{pm.get_text('seconds')}"
        click.echo(f"\n{Fore.GREEN}✓ 已成功删除记录{Style.RESET_ALL} ({delete_time_text})")
    else:
        click.echo(f"\n{Fore.RED}✗ 删除失败{Style.RESET_ALL} ({delete_time:.3f}秒)")

@cli.command()
@click.option('--path', '-p', required=True, help=get_help_text('help_export_path'))
def export(path):
    """Export passwords to a file.
    
    Arguments:
        path: The path where to save the exported passwords
    """
    pm = PasswordManager()
    
    try:
        export_path = validate_export_path(path)
        start_time = time.time()
        pm.export_passwords(export_path)
        export_time = time.time() - start_time
        
        export_time_text = f"{export_time:.3f}{pm.get_text('seconds')}"
        click.echo(f"\n{Fore.GREEN}✓ 密码已成功导出到: {export_path}{Style.RESET_ALL} ({export_time_text})")
    except click.ClickException as e:
        click.echo(f"\n{Fore.RED}✗ 导出失败: {e.message}{Style.RESET_ALL}")

@cli.command()
@click.option('--path', '-p', required=True, help=get_help_text('help_import_path'))
def import_passwords(path):
    """Import passwords from a file.
    
    Arguments:
        path: The path of the file to import passwords from
    """
    if not os.path.exists(path):
        click.echo(f"\n{Fore.RED}✗ {pm.get_text('file_not_exists').format(path)}{Style.RESET_ALL}")
        return

    pm = PasswordManager()
    
    try:
        start_time = time.time()
        pm.import_passwords(path)
        import_time = time.time() - start_time
        
        import_time_text = f"{import_time:.3f}{pm.get_text('seconds')}"
        click.echo(f"\n{Fore.GREEN}✓ 已成功从 {path} 导入密码{Style.RESET_ALL} ({import_time_text})")
    except Exception as e:
        click.echo(f"\n{Fore.RED}✗ 导入失败: {str(e)}{Style.RESET_ALL}")

@cli.command()
def clear():
    """Clear all passwords"""
    pm = PasswordManager()
    
    # 先显示当前记录数
    passwords = pm.get_passwords()
    if not passwords:
        click.echo(f"\n{Fore.YELLOW}{pm.get_text('no_records_in_db')}{Style.RESET_ALL}")
        return
    
    click.echo(f"\n{Fore.RED}{pm.get_text('warning_delete_all').format(len(passwords))}{Style.RESET_ALL}")
    click.echo(f"\n{Fore.YELLOW}{pm.get_text('existing_records')}{Style.RESET_ALL}")
    
    # 显示所有记录的简要信息
    for p in passwords:
        click.echo(f"{Fore.BLUE}ID{Style.RESET_ALL} {p['id']}, {Fore.BLUE}账号{Style.RESET_ALL} {p['account']}")
    
    # 双重确认
    click.echo(f"\n{Fore.RED}{pm.get_text('operation_irreversible')}{Style.RESET_ALL}")
    if not click.confirm(f"{Fore.RED}{pm.get_text('confirm_clear_all')}{Style.RESET_ALL}", default=False):
        click.echo(f"\n{Fore.YELLOW}{pm.get_text('clear_cancelled')}{Style.RESET_ALL}")
        return
    
    if not click.confirm(f"{Fore.RED}{pm.get_text('confirm_clear_all_again')}{Style.RESET_ALL}", default=False):
        click.echo(f"\n{Fore.YELLOW}{pm.get_text('clear_cancelled')}{Style.RESET_ALL}")
        return
    
    start_time = time.time()
    success = pm.clear_all_passwords()  # 需要在 PasswordManager 中实现此方法
    clear_time = time.time() - start_time
    
    if success:
        clear_time_text = f"{clear_time:.3f}{pm.get_text('seconds')}"
        click.echo(f"\n{Fore.GREEN}✓ 已成功清空所有记录{Style.RESET_ALL} ({clear_time_text})")
    else:
        click.echo(f"\n{Fore.RED}✗ 清空操作失败{Style.RESET_ALL} ({clear_time:.3f}秒)")

def validate_export_path(path: str) -> str:
    """验证并处理导出路径"""
    # 如果只提供了目录，添加默认文件名
    if path.endswith('/') or path.endswith('\\') or os.path.isdir(path):
        path = os.path.join(path, f'passwords_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
    
    # 确保目录存在
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        try:
            os.makedirs(directory)
        except PermissionError:
            raise click.ClickException(pm.get_text('no_permission_dir').format(directory))
    
    # 测试文件是否可写
    try:
        with open(path, 'a') as f:
            pass
        return path
    except PermissionError:
        raise click.ClickException(pm.get_text('no_permission_file').format(path))
    except OSError as e:
        raise click.ClickException(pm.get_text('invalid_path').format(e))

def check_back(value: str) -> bool:
    """检查是否要返回主菜单"""
    return value.lower() == 'b'

if __name__ == '__main__':
    cli() 