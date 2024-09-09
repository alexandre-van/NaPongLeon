import { useState } from 'react';

//import { API_BASE_URL } from '../config.js';

export default function SelectFactionForm({ navigate }) {
 // const [faction, setFaction] = useState({
  //  faction: '',
 // });

  // maybe for form 
/*  const handleRegister = async (userData) => {
    try {
      const response = await fetch(`$(API_BASE_URL)/api/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userData),
      });
      if (response.ok) {
        setRegistrationStatus('success');
      } else {
        setRegistrationStatus('failure');
      }
    } catch (error) {
      console.error('Error while sign up:', error);*/

  return (
    <div>
    <h1>SELECT YOUR FACTION</h1>
    <label>BRITISH</label>
    <label>FRENCH</label>
    <label>RUSSIAN</label>
    </div>
  );
}
