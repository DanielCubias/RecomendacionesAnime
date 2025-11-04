import { useState } from "react";

function Login({ onLoginSuccess }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [username, setUsername] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [message, setMessage] = useState("");
  const [isRegistering, setIsRegistering] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validación de contraseñas en registro
    if (isRegistering && password !== confirmPassword) {
      setMessage("Las contraseñas no coinciden.");
      return;
    }

    const url = isRegistering
      ? "http://localhost:5000/auth/register"
      : "http://localhost:5000/auth/login";

    const payload = isRegistering
      ? { username, email, password }
      : { email, password };

    try {
      const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await res.json();

      if (res.ok) {
        if (isRegistering) {
          setMessage("Cuenta creada con éxito 🎉, ahora inicia sesión.");
          setIsRegistering(false);
          // Limpiar campos después del registro
          setUsername("");
          setEmail("");
          setPassword("");
          setConfirmPassword("");
        } else {
          localStorage.setItem("token", data.token);
          localStorage.setItem("username", data.username);
          onLoginSuccess();
        }
      } else {
        setMessage(data.error || "Error al procesar la solicitud.");
      }
    } catch (err) {
      setMessage("Error de conexión con el servidor.");
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h1 style={styles.title}>
          {isRegistering ? "Crear Cuenta" : "Iniciar Sesión"}
        </h1>
        <form onSubmit={handleSubmit} style={styles.form}>
          {isRegistering && (
            <input
              type="text"
              placeholder="Nombre de usuario"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              style={styles.input}
              required
            />
          )}
          <input
            type="email"
            placeholder="Correo electrónico"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            style={styles.input}
            required
          />
          <input
            type="password"
            placeholder="Contraseña"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            style={styles.input}
            required
          />
          {isRegistering && (
            <input
              type="password"
              placeholder="Confirmar contraseña"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              style={styles.input}
              required
            />
          )}
          <button type="submit" style={styles.button}>
            {isRegistering ? "Registrarse" : "Entrar"}
          </button>
        </form>
        <p style={styles.text}>
          {isRegistering ? "¿Ya tienes cuenta? " : "¿No tienes cuenta? "}
          <span
            onClick={() => {
              setIsRegistering(!isRegistering);
              setMessage("");
            }}
            style={styles.link}
          >
            {isRegistering ? "Inicia sesión" : "Regístrate aquí"}
          </span>
        </p>
        {message && <p style={styles.message}>{message}</p>}
      </div>
    </div>
  );
}

const styles = {
  container: {
    height: "100vh",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    background: "linear-gradient(135deg, #0f0c29, #302b63, #24243e)",
    color: "#fff",
  },
  card: {
    backgroundColor: "rgba(0, 0, 0, 0.7)",
    padding: "40px",
    borderRadius: "15px",
    boxShadow: "0 0 15px #00ffff",
    textAlign: "center",
    width: "350px",
  },
  title: {
    marginBottom: "20px",
    fontSize: "24px",
    textShadow: "0 0 10px #00ffff",
  },
  form: {
    display: "flex",
    flexDirection: "column",
  },
  input: {
    padding: "10px",
    margin: "10px 0",
    borderRadius: "5px",
    border: "none",
    outline: "none",
    backgroundColor: "#1e1e2f",
    color: "#fff",
    fontSize: "16px",
  },
  button: {
    marginTop: "10px",
    padding: "10px",
    backgroundColor: "#00ffff",
    color: "#000",
    border: "none",
    borderRadius: "5px",
    cursor: "pointer",
    fontWeight: "bold",
    transition: "0.3s",
  },
  link: {
    color: "#00ffff",
    cursor: "pointer",
    textDecoration: "underline",
  },
  text: {
    marginTop: "15px",
  },
  message: {
    marginTop: "10px",
    color: "#ff6b6b",
  },
};

export default Login;