import React, { useEffect, useState } from 'react';
import { Button, Dialog, DialogActions, DialogContent, DialogTitle, MenuItem, TextField, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper } from '@mui/material';


function AdminButtons() {

    const [isAuthorized, setIsAuthorized] = useState(false);

    const [openAddPlayer, setOpenAddPlayer] = useState(false);
    const [openRecordMatch, setOpenRecordMatch] = useState(false);
    const [playerName, setPlayerName] = useState('');
    const [players, setPlayers] = useState([]);
    const [winner, setWinner] = useState('');
    const [loser, setLoser] = useState('');

    // Replace this with your actual API call
    const fetchPlayers = async () => {
        console.info('Fetching players')
        try {
            const response = await fetch('https://elo.alberthyang.com:8000/players');
            if (!response.ok) {
            throw new Error('Players data fetch failed');
            }
            const data = await response.json();
            console.info(data);
            setPlayers(data.players);
        } catch (error) {
            console.error('Error fetching players:', error);
        }
    };

    useEffect(() => {
        fetchPlayers();
      }, []);

    const handleAddPlayer = async () => {
        try {
            const response = await fetch('https://elo.alberthyang.com:8000/add_player', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({'name': playerName})
            });
            window.location.reload(true);
        } catch (error) {
            console.error('Error adding new player:', error)
        }
    }

    const handleRecordMatch = async () => {
        try {
            const response = await fetch('https://elo.alberthyang.com:8000/match', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({'winner': winner, 'loser': loser})
            })
            window.location.reload(true)
        } catch (error) {
            console.error('Error recording match:', error)
        }
    }

    useEffect(() => {
      const checkAuthorization = async () => {
        const token = localStorage.getItem('jwtToken');
        if (token == null) {
            console.info('No token. Exiting auth.')
            setIsAuthorized(false);
            return;
        }

        try {
          const response = await fetch('https://elo.alberthyang.com:8000/is_authorized', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
          });
          if (response.ok) {
            setIsAuthorized(true);
            console.info('Successful token auth.')
          }
        } catch (error) {
          console.error('Authorization check failed:', error);
        }
      };
    
      checkAuthorization();
    }, []);

    return <div>
        <Button variant="contained" onClick={() => setOpenAddPlayer(true)} style={{ margin: 10 }} sx={{display: isAuthorized?null:'none'}}>
        Add Player
        </Button>
        
        <Dialog open={openAddPlayer} onClose={() => setOpenAddPlayer(false)}>
        <DialogTitle>Add Player</DialogTitle>
        <DialogContent>
            <TextField
            autoFocus
            margin="dense"
            id="playerName"
            label="Name"
            type="text"
            fullWidth
            value={playerName}
            onChange={(e) => setPlayerName(e.target.value)}
            />
        </DialogContent>
        <DialogActions>
            <Button onClick={() => setOpenAddPlayer(false)}>Cancel</Button>
            <Button onClick={() => handleAddPlayer()}>Add Player</Button>
        </DialogActions>
        </Dialog>
        
        <Button variant="contained" onClick={() => setOpenRecordMatch(true)} style={{ margin: 10 }} sx={{display: isAuthorized?null:'none'}}>
        Record Match
        </Button>
        
        <Dialog open={openRecordMatch} onClose={() => setOpenRecordMatch(false)}>
        <DialogTitle>Record Match</DialogTitle>
        <DialogContent>
        <TextField
            select
            label="Winner"
            value={winner}
            onChange={(e) => setWinner(e.target.value)}
            fullWidth
            margin="dense"
        >
        {players.filter(p => p !== loser).map((player) => (
            <MenuItem key={player.name} value={player.name}>{player.name}</MenuItem>
        ))}
        </TextField>
        
        <TextField
            select
            label="Loser"
            value={loser}
            onChange={(e) => setLoser(e.target.value)}
            fullWidth
            margin="dense"
        >
        {players.filter(p => p !== winner).map((player) => (
            <MenuItem key={player.name} value={player.name}>{player.name}</MenuItem>
        ))}
        </TextField>
        </DialogContent>
        <DialogActions>
            <Button onClick={() => setOpenRecordMatch(false)}>Cancel</Button>
            <Button onClick={() => handleRecordMatch()}>Record Match</Button>
        </DialogActions>
        </Dialog>

    </div>

}

export default AdminButtons;
