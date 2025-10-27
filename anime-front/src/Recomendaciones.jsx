import React from "react";

const Recomendaciones = ({ animesList, onClose, selectedAnimesLength }) => {

    const entries = animesList ? Object.entries(animesList) : [];
    const orderedEntries = entries.sort((a, b) => b[1] - a[1]);

    return (
        <div style={styles.bg} onClick={onClose}>
            {entries.length > 0 ? (
                <div
                    style={styles.modal}
                    onClick={(e) => e.stopPropagation()} // prevent closing when clicking modal
                >
                    <h2 style={styles.title}>Recomendaciones de Anime</h2>
                    <div style={styles.animeList}>
                        {orderedEntries.map(([title, score], index) => (
                            <div key={index} style={styles.anime}>
                                - {title}, Score: {(score * 10 / selectedAnimesLength).toFixed(2) + " %"}
                            </div>
                        ))}
                    </div>
                </div>
            ) : (
                <div style={styles.spinnerContainer}>
                    <div style={styles.spinner}></div>
                </div>
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
        zIndex: 9999,
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
        justifyContent: 'center',
        alignItems: 'center',
        textAlign: 'center',
        cursor: 'default'
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
    },
    spinnerContainer: {
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100%',
    },
    spinner: {
        border: '6px solid rgba(255, 255, 255, 0.2)',
        borderTop: '6px solid white',
        borderRadius: '50%',
        width: '50px',
        height: '50px',
        animation: 'spin 1s linear infinite',
    },
};
