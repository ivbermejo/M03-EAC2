from django.test import LiveServerTestCase
from selenium import webdriver
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
        # Forzamos un tamaño de ventana estándar para evitar errores de renderizado
        opts.add_argument('--width=1920')
        opts.add_argument('--height=1080')
        
        cls.selenium = webdriver.Firefox(options=opts)

        # Crear superusuario para el test
        User.objects.create_superuser("isard", "isard@isardvdi.com", "pirineus")

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_crear_usuari_staff_via_admin(self):
        wait = WebDriverWait(self.selenium, 15) # Un poco más de margen para el servidor de GitHub

        # 1. Login
        self.selenium.get(f"{self.live_server_url}/admin/login/")
        
        user_input = wait.until(EC.presence_of_element_located((By.NAME, "username")))
        user_input.send_keys("isard")
        
        self.selenium.find_element(By.NAME, "password").send_keys("pirineus")
        self.selenium.find_element(By.XPATH, "//input[@type='submit']").click()

        # 2. Añadir Usuario
        # Esperamos a que cargue el dashboard y vamos directo a la URL de alta
        wait.until(EC.presence_of_element_located((By.ID, "content-main")))
        self.selenium.get(f"{self.live_server_url}/admin/auth/user/add/")

        u_field = wait.until(EC.presence_of_element_located((By.ID, "id_username")))
        u_field.send_keys("staff_selenium")

        # IDs para contraseñas en Django moderno
        self.selenium.find_element(By.ID, "id_password1").send_keys("StaffPass123!")
        self.selenium.find_element(By.ID, "id_password2").send_keys("StaffPass123!")
        self.selenium.find_element(By.NAME, "_save").click()

        # 3. Permisos de Staff
        # En la ficha de edición, activamos el checkbox
        staff_chkbx = wait.until(EC.presence_of_element_located((By.ID, "id_is_staff")))
        if not staff_chkbx.is_selected():
            staff_chkbx.click()

        self.selenium.find_element(By.NAME, "_save").click()

        # 4. Verificación final
        wait.until(EC.presence_of_element_located((By.ID, "result_list")))
        self.assertTrue("staff_selenium" in self.selenium.page_source)

# Create your tests here.
