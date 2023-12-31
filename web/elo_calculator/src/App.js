import React, { useEffect, useState } from 'react';
import { Button, Dialog, DialogActions, DialogContent, DialogTitle, TextField, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper } from '@mui/material';
import AdminButtons from './AdminButtons';
import LoginButton from './LoginButton';

function App() {

  const [summary, setSummary] = useState({ ordered_players: [], match_history: []});

  useEffect(() => {
    fetch('http://localhost:8000/summary')
      .then(response => response.json())
      .then(data => {
        let thing = JSON.parse(data.response_json_str)
        setSummary(thing)
      })
      .catch(error => console.error('Error fetching data:', error));
  }, [])

  return (
    <div>
      <LoginButton/>
      <AdminButtons/>

      <h1>Elo Summary</h1>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell align="right">Elo</TableCell>
              <TableCell align="right">Wins</TableCell>
              <TableCell align="right">Losses</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {summary.ordered_players.map((player) => (
              <TableRow key={player.name}>
                <TableCell component="th" scope="row">{player.name}</TableCell>
                <TableCell align="right">{player.elo}</TableCell>
                <TableCell align="right">{player.win}</TableCell>
                <TableCell align="right">{player.loss}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <h1>Match History</h1>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Winner</TableCell>
              <TableCell>Loser</TableCell>
              <TableCell>Date</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {summary.match_history.map((match, index) => (
              <TableRow key={index}>
                <TableCell>{match.winner}</TableCell>
                <TableCell>{match.loser}</TableCell>
                <TableCell>{match.date}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </div>
  );
}

export default App;
