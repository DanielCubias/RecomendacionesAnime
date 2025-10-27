import React, { useState, useEffect } from "react";
import "/src/index.css"
import Recomendaciones from "./Recomendaciones";

// puntuacion por defecto

export default function AnimeRatingApp() {
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
        setAnimes(data.data);
        setLoading(false);
      } catch (err) {
        console.error("Error al obtener los animes:", err);
      }
    };

    fetchAnimes();
  }, [limit]);

  // Seleccionar o deseleccionar un anime
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

  const handleGetRecommendations = async () => {
  console.log("Animes seleccionados para recomendaciones:", selectedAnimes);
  if (Object.keys(selectedAnimes).length === 0) {
    alert("Por favor, selecciona al menos un anime y asigna una puntuación.");
    return;
  }
  setCalled(true);

  const formattedData = {
    ratings: Object.entries(selectedAnimes).map(([id, anime]) => ({
      name: anime.title,
      rating: parseFloat(anime.score),
    })),
  };

  try {
    const response = await fetch("http://localhost:5000/anime/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(formattedData),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    const data = await response.json();
    console.log("Recomendaciones recibidas:", data);

    // 👇 Guardamos las recomendaciones recibidas
    setRecommendations(data || {});
  } catch (err) {
    console.error("Error al obtener recomendaciones:", err);
    setCalled(false);
  }
};


  return (
    <div className="p-6 max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold text-center mb-4">Puntúa tus animes favoritos 🎌</h1>
      <button
        onClick={handleGetRecommendations}>Coger recomendaciones</button>

        
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
       <div className="text-center mb-6 mt-8 py-4">
        <label className="mr-2 font-medium">Mostrar:</label>
        <select
          value={limit}
          onChange={(e) => setLimit(Number(e.target.value))}
          className="border p-2 rounded"
        >
          <option value="10">10</option>
          <option value="20">20</option>
          <option value="50">50</option>
        </select>
        <span className="ml-2">animes</span>
      </div>

      {loading && <p className="text-center">Cargando animes...</p>}

      {/* Lista de animes */}
      
 {!loading && (
  <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-8"> {/* Más espacio entre tarjetas */}
    {animes.map((anime) => (
      <div
        key={anime.mal_id}
        className="anime-card p-4 hover:shadow-lg transition"
      >
        <img
          src={anime.images.jpg.image_url}
          alt={anime.title}
          className="w-full h-72 object-cover rounded" // Imagen más alta
        />
        <div className="mt-4 flex flex-col items-center">
          <p className="font-semibold text-center text-sm mb-3">{anime.title}</p>

          <label className="flex items-center gap-10 text-sm mb-3"> {/* Más espacio entre checkbox y texto */}
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
              className="border rounded w-20 text-center mt-4" // Separación y ancho extra
            />
          )}
        </div>
      </div>
    ))}
  </div>
)}





{/* Recomendaciones */}
{called && <Recomendaciones animesList={recommendations} />}


    </div>
  );
}
