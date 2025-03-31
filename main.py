import re
from helpers.utils import *
from datetime import datetime
import pandas as pd
from playwright.sync_api import sync_playwright
from env.env import *

def main():
    start_time = start_count_time()
    list_info_courses = []
    data_atual = datetime.now().strftime('%Y_%m_%d')

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        try:
            print(f'Step - Accessing {URL}')
            page.goto(URL)

            # Preenchendo o campo email
            email_selector = 'input[placeholder="Email"]'
            page.wait_for_selector(email_selector)
            page.fill(email_selector, USER)
            print(f'Step - Email filled')

            # Preenchendo o campo senha
            password_selector = 'input[placeholder="Senha"]'
            page.wait_for_selector(password_selector)
            page.fill(password_selector, PASSWORD)
            print(f'Step - Password filled')

            # Clicando no botão entrar
            button_enter_selector = 'button:has-text("ENTRAR")'
            page.wait_for_selector(button_enter_selector)
            page.click(button_enter_selector)
            print(f'Step - Button ENTRAR clicked')

            # Confirmando login
            confirm_login_selector = 'li[id="wp-admin-bar-my-account"]'
            page.wait_for_selector(confirm_login_selector)
            user_text = page.locator(confirm_login_selector).inner_text()
            print(f'Step - User logged: {user_text}')

            # Acessando página dos cursos
            page.goto(URL_COURSE_PAGE)
            confirm_page_course_selector = 'a:has-text("Courses")'
            page.wait_for_selector(confirm_page_course_selector)
            print(f'Step - Page course found!')

            # Identificando quantas páginas de curso existem
            total_pages = int(page.evaluate('document.querySelectorAll(\'a.page-numbers\').length'))
            print(f'Step - {total_pages} pages found!')

            # Navegando pelas paginas > detalhes para buscar dados
            for i in range(total_pages):
                current_page_url = f'https://espacosinovativos.inovatecjp.com.br/wp-admin/admin.php?paged={i + 1}&page=tutor_report&sub_page=courses'
                page.goto(current_page_url, wait_until='networkidle')
                page.wait_for_selector(confirm_page_course_selector)
                print(f'\nStep - scraping data from page {i+1}')

                # Capturando a quantidade de botões 'Details' da pagina
                len_details = len(page.query_selector_all('a:has-text("Details")'))

                # Iterando a lista e clicando em cada botão
                for i in range(len_details):
                    list_details_course = page.query_selector_all('a:has-text("Details")')
                    list_details_course[i].click()

                    # Capturando o nome do curso
                    selector_course_name = 'div[id="tutor-report-courses-details-wrap"]'
                    page.wait_for_selector(selector_course_name)
                    course_name = page.locator(selector_course_name).inner_text().split('\n')[0]

                    # Capturando o valor de "Courses Completed' com regex
                    seletor_info_page = 'div[id="wpbody-content"]'
                    info_page = page.query_selector(seletor_info_page).inner_text()
                    match = re.search(r'Students\s*(\d+)', info_page)

                    if match:
                        courses_completed = match.group(1)
                    else:
                        courses_completed = None

                    info_course = {'course_name': course_name, 'total_certificates': courses_completed}
                    print(f'Course {i+1}/{len_details} | {info_course}')
                    list_info_courses.append(info_course)

                    page.goto(current_page_url, wait_until='networkidle')
                    page.wait_for_selector(confirm_page_course_selector)

            print(f'\nStep - Data from {len(list_info_courses)} courses successfully collected.')

        except Exception as e:
            print(f'An error occurred: {e}')
        finally:
            browser.close()
            execution_time = end_count_time(start_time)
            #print(f'Cursos buscados: {list_info_courses}')

    # Salvando a lista em uma planilha Excel
    df = pd.DataFrame(list_info_courses)
    df.to_excel(f'output/relatorio_{data_atual}.xlsx', index=False)
    print(f'Data saved to output/relatorio_{data_atual}.xlsx')
    print(f'\nTotal execution time: {execution_time}')


if __name__ == "__main__":
    main()
