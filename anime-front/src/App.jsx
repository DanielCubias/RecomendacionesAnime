import React, { useState, useEffect } from "react";
import "/src/index.css";
import Recomendaciones from "./Recomendaciones";
import Login from "./login";

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(
    false
  );

  const handleLoginSuccess = () => {
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    // Eliminar datos del localStorage
    localStorage.removeItem("token");
    localStorage.removeItem("username");
    
    // Cambiar estado para volver al login
    setIsAuthenticated(false);
  };

  return (
    <>
      {isAuthenticated ? (
        <AnimeRatingApp onLogout={handleLogout} />
      ) : (
        <Login onLoginSuccess={handleLoginSuccess} />
      )}
    </>
  );
}

// Componente principal de la app (solo UI, no maneja auth)
function AnimeRatingApp({ onLogout }) {
  const [animes, setAnimes] = useState([]);
  const [selectedAnimes, setSelectedAnimes] = useState({});
  const [limit, setLimit] = useState(10);
  const [loading, setLoading] = useState(true);
  const [recommendations, setRecommendations] = useState({});
  const [called, setCalled] = useState(false);
  



  //  Obtener los animes desde la API
  useEffect(() => {
    const fetchAnimes = async () => {
      try {
        setLoading(true);
        const response = await fetch(`https://api.jikan.moe/v4/anime?limit=${limit}`);
        const data = await response.json();
        setAnimes(data.data || []);
        setLoading(false);
      } catch (err) {
        console.error("Error al obtener los animes:", err);
        setLoading(false);
      }
    };
    getInitialRatings();
    fetchAnimes();
  }, [limit]);

  // Seleccionar/deseleccionar anime
  const toggleAnimeSelection = (anime) => {
    setSelectedAnimes((prev) => {
      const newSelection = { ...prev };
      if (newSelection[anime.mal_id]) {
        delete newSelection[anime.mal_id];
      } else {
        newSelection[anime.mal_id] = { title: anime.title, score: 0 };
      }
      return newSelection;
    });
  };

  // Cambiar puntuación
  const handleScoreChange = (animeId, value) => {
    setSelectedAnimes((prev) => ({
      ...prev,
      [animeId]: { ...prev[animeId], score: parseFloat(value) },
    }));
  };

  // Send review to backend
  try {
    const response = await fetch("http://localhost:5000/rate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(formattedData),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    const data = await response.json();
    console.log("Review enviada:", data);

  } catch (err) {
    console.error("Error al subir rate:", err);
  }
};

const getInitialRatings = async () => {
  try {
    const response = await fetch("http://localhost:5000/user_ratings/"+localStorage.getItem("userId"), {
      method: "GET",
      headers: { "Content-Type": "application/json" },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    const data = await response.json();

    // 👇 Guardamos las recomendaciones recibidas
    console.log("Initial ratings received:", data);
    setSelectedAnimes(Object.values(data) || {});
  } catch (err) {
    console.error("Error al obtener recomendaciones:", err);
    setCalled(false);
  }
}


  const handleGetRecommendations = async () => {
    if (Object.keys(selectedAnimes).length === 0) {
      alert("Por favor, selecciona al menos un anime y asigna una puntuación.");
      return;
    }
  
    setCalled(true);

  try {
    const response = await fetch("http://localhost:5000/recommend/"+localStorage.getItem("userId"), {
      method: "GET",
      headers: { "Content-Type": "application/json" },
    });

      if (!response.ok) throw new Error(`Error: ${response.status}`);

      const data = await response.json();
      setRecommendations(data || {});
    } catch (err) {
      console.error("Error al obtener recomendaciones:", err);
      setCalled(false);
    }
  };

const closeRecommendations = () => {
  setCalled(false);
  setRecommendations({});
}


  return (
    <div className="p-6 max-w-5xl mx-auto">
      {/* Header con botón de logout */}
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">🎌 Puntúa tus animes favoritos 🎌</h1>
        <button
          onClick={onLogout}
          className="bg-red-500 hover:bg-red-600 text-white font-medium py-2 px-4 rounded transition"
        >
          Cerrar Sesión
        </button>
      </div>

      <button
        onClick={handleGetRecommendations}
        className="mb-6 bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-6 rounded transition"
      >
        Obtener Recomendaciones
      </button>

      {/* Resumen de puntuaciones */}
      {Object.keys(selectedAnimes).length > 0 && (
        <div className="mt-8 bg-gray-100 p-4 rounded-xl">
          <h2 className="text-xl font-bold mb-2">🎯 Animes puntuados:</h2>
          <ul className="list-disc ml-5">
            {Object.entries(selectedAnimes).map(([id, anime]) => (
              <li key={id}>
                {anime.title}: <strong>{anime.score}</strong>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Control de cantidad */}
      <div className="text-center py-4" style={{ margin: "10px 0" }}>
        <label className="mr-2 font-medium">Mostrar: </label>
        <select
          value={limit}
          onChange={(e) => setLimit(Number(e.target.value))}
          className="border p-2 rounded"
        >
          <option value="10">10</option>
          <option value="20">20</option>
        </select>
        <span className="ml-2">animes</span>
      </div>

      {/* Lista de animes */}
      {loading ? (
        <p className="text-center">Cargando animes...</p>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-6">
          {animes.map((anime) => (
            <div
              key={anime.mal_id}
              className="anime-card p-4 hover:shadow-lg transition bg-white rounded-lg shadow"
            >
              <img
                src={anime.images.jpg.image_url}
                alt={anime.title}
                className="w-full h-72 object-cover rounded"
              />
              <div className="mt-4 flex flex-col items-center">
                <p className="font-semibold text-center text-sm mb-3">{anime.title}</p>

                <label className="flex items-center gap-2 text-sm mb-3">
                  <input
                    type="checkbox"
                    checked={!!selectedAnimes[anime.mal_id]}
                    onChange={() => toggleAnimeSelection(anime)}
                  />
                  Seleccionar
                </label>

                {selectedAnimes[anime.mal_id] && (
                  <input
                    type="number"
                    min="1"
                    max="10"
                    value={selectedAnimes[anime.mal_id].score}
                    onChange={(e) => handleScoreChange(anime.mal_id, e.target.value)}
                    className="border rounded w-20 text-center mt-2 p-1"
                    placeholder="1-10"
                  />
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Recomendaciones */}
      {called && (
        <Recomendaciones
          animesList={recommendations}
          selectedAnimesLength={Object.keys(selectedAnimes).length}
          onClose={closeRecommendations}
        />
      )}
    </div>
  );
}

// Exportar App como componente principal
export default App;