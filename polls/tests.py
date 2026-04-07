from django.test import LiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.contrib.auth.models import User

class MySeleniumTests(LiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        opts = Options()
        opts.add_argument('--headless')
        cls.selenium = WebDriver(options=opts)
        
        # Superusuario inicial
        User.objects.create_superuser("isard", "isard@isardvdi.com", "pirineus")

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_crear_usuari_staff_via_admin(self):
        wait = WebDriverWait(self.selenium, 10)
        
        # 1. Login
        self.selenium.get(f"{self.live_server_url}/admin/login/")
        wait.until(EC.presence_of_element_located((By.NAME, "username"))).send_keys("isard")
        self.selenium.find_element(By.NAME, "password").send_keys("pirineus")
        self.selenium.find_element(By.XPATH, "//input[@type='submit']").click()

        # 2. Añadir Usuario
        # Forzamos la carga de la página de "add" para evitar perdernos
        self.selenium.get(f"{self.live_server_url}/admin/auth/user/add/")
        
        # Esperamos a que el campo username de la ficha de alta aparezca
        u_field = wait.until(EC.presence_of_element_located((By.ID, "id_username")))
        u_field.send_keys("staff_selenium")
        
        # IMPORTANTE: En Django 5.2 los IDs son id_password1 e id_password2
        self.selenium.find_element(By.ID, "id_password1").send_keys("StaffPass123!")
        self.selenium.find_element(By.ID, "id_password2").send_keys("StaffPass123!")
        self.selenium.find_element(By.NAME, "_save").click()

        # 3. Permisos de Staff (estamos en la ficha de edición)
        # Buscamos el checkbox por ID, que es infalible
        staff_chkbx = wait.until(EC.presence_of_element_located((By.ID, "id_is_staff")))
        if not staff_chkbx.is_selected():
            staff_chkbx.click()
            
        self.selenium.find_element(By.NAME, "_save").click()

        # 4. Verificación
        # Buscamos que el nombre aparezca en la lista final
        wait.until(EC.presence_of_element_located((By.ID, "result_list")))
        assert "staff_selenium" in self.selenium.page_source

# Create your tests here.
