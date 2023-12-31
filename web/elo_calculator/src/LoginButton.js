import React, { useEffect, useState } from 'react';
import { Button, Dialog, DialogActions, DialogContent, DialogTitle, TextField, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper } from '@mui/material';

function LoginButton() {

    const [open, setOpen] = useState(false);
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');

    const handleClickOpen = () => {
        setOpen(true);
      };
    
    const handleClose = () => {
        setOpen(false);
    };

    const handleLogin = async () => {
        try {
          const response = await fetch('/token', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `grant_type=password&username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`,
        });
    
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
    
        const data = await response.json();
        if (data.access_token == null) {
            throw new Error('Failed to login')
        }
            localStorage.setItem('jwtToken', data.access_token);
            handleClose();
        } catch (error) {
            console.error('Login failed:', error);
        }
    };

    return <div>
      <Button variant="contained" color="primary" onClick={handleClickOpen} style={{ position: 'absolute', top: 10, right: 10 }}>
        Login
      </Button>
      <Dialog open={open} onClose={handleClose}>
        <DialogTitle>Login</DialogTitle>
        <DialogContent>
          <TextField autoFocus margin="dense" id="username" label="Username" type="text" fullWidth variant="standard" onChange={(e) => setUsername(e.target.value)}/>
          <TextField margin="dense" id="password" label="Password" type="password" fullWidth variant="standard" onChange={(e) => setPassword(e.target.value)}/>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
          <Button onClick={handleLogin}>Login</Button>
        </DialogActions>
      </Dialog>
    </div>
}

export default LoginButton;
