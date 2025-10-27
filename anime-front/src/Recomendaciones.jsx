import React from "react";

const Recomendaciones = ({ animesList }) => {
    console.log("Animes recibidos para mostrar recomendaciones:", animesList);

    const entries = animesList ? Object.entries(animesList) : [];

    return (
        <div style={styles.bg}>
            {entries.length > 0 ? (
                <div style={styles.modal}>
                    <h2 style={styles.title}>Recomendaciones de Anime</h2>
                    <div style={styles.animeList}>
                        {entries.map(([title, score], index) => (
                            <div key={index} style={styles.anime}>
                                - {title}, Score: {(score * entries.length).toFixed(2) + " %"}
                            </div>
                        ))}
                    </div>
                </div>
            ) : (
                "Cargando..."
            )}
        </div>
    );
};

export default Recomendaciones;

const styles = {
    bg: {
        position: 'fixed',       
        top: 0,
        left: 0,
        width: '100vw',
        height: '100vh',
        backgroundColor: 'rgba(0, 0, 0, 0.5)', 
        display: 'flex',         
        justifyContent: 'center',
        alignItems: 'center',
        zIndex: 9999
    },
    modal: {
        backgroundColor: 'black',
        width: '50%',
        height: '50%',
        borderRadius: '15px',    
        padding: '20px',
        boxShadow: '0 4px 20px rgba(108, 5, 120, 0.3)',
        overflowY: 'auto',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',  // vertical center
        alignItems: 'center',      // horizontal center
        textAlign: 'center'        // center text inside
    },
    title: {
        color: 'white',
        fontSize: '1.5rem',
        fontWeight: 'bold',
        marginBottom: '20px'
    },
    anime: {
        padding: '10px',
        color: 'white'
    },
    animeList: {
        maxHeight: '80%',
        width: '100%'
    }
};
