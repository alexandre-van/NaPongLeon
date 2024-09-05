import { useState } from 'react';
import SpecialLayout from '../layouts/SpecialLayout.js';
import RegisterForm from '../components/RegisterForm.js';
import SelectFaction from '../components/SelectFaction.js';
import RegisterFailure from '../components/RegisterFailure.js';

import { API_BASE_URL } from '../config.js';

export default function RegisterPage({ navigate }) {
  const [registrationStatus, setRegistrationStatus] = useState(null);

  const handleRegister = async (userData) => {
    try {
      const response = await fetch(`/api/authentication/register/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userData),
      });
      console.log('Response status:', response.status);
      console.log('Response headers:', response.headers);
      const responseBody = await response.text();
      console.log('Response body:', responseBody);

      if (response.ok) {
        setRegistrationStatus('success');
      } else {
        setRegistrationStatus('failure');
      }
    } catch (error) {
      console.error('Error while sign up:', error);
      setRegistrationStatus('failure');
    }
  };

  return (
    <SpecialLayout navigate={navigate}>
      {registrationStatus === 'success' ? (
        <SelectFaction navigate={navigate} />
      ) : registrationStatus === 'failure' ? (
        <RegisterFailure onRegister={handleRegister} />
      ) : (
        <RegisterForm onRegister={handleRegister} /> 
      )}
    </SpecialLayout>
  );
}
