# 🎌 RecomendacionesAnime

Sistema de recomendaciones de anime basado en valoraciones de usuario, utilizando **Flask** (BackEnd) y **Vite + React** (FrontEnd).

---

## ⚙️ Iniciar BackEnd

1. Abrir un terminal dentro de la carpeta **`anime-back`**
2. Instalar las librerías necesarias:
   ```bash
   pip install -r requirements.txt
   ```
3. Iniciar el servidor BackEnd con:
   ```bash
   flask --app api.py run
   ```
4. El servidor se ejecutará por defecto en:
   ```bash
   http://127.0.0.1:5000
   ```

## 💻 Iniciar FrontEnd

1. Abrir un terminal dentro de la carpeta **`anime-front`**
2. Instalar las dependencias necesarias:
   ```bash
   npm i
   ```
3. Iniciar el servidor FrontEnd:
   ```bash
   npm run dev
   ```
4. Una vez iniciado, el comando anterior mostrará un enlace como el siguiente:
   ```bash
   http://localhost:5173/
   ```

## 🎮 Interactuar con la Web

1. Se mostrará una lista con varios animes disponibles.
2. Selecciona uno o varios animes y asigna una puntuación a cada uno (por defecto la puntuación es 0).
3. Haz clic en el botón “Coger recomendaciones”.
4. En pocos instantes, aparecerá un modal con tus recomendaciones personalizadas.
5. Si deseas obtener recomendaciones distintas:
   - Cierra el modal haciendo clic fuera de él.
   - Repite el proceso desde el paso 2.
