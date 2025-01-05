import { useState } from 'react';
import { Button, Form, Alert } from 'react-bootstrap'; // Importation de Alert pour les messages
import { useUser } from '../contexts/UserContext.js';

export default function ForcedPasswordPage() {
  const [formData, setFormData] = useState({
    email: '',
  });
  const { resetPassword } = useUser();
  const [successMessage, setSuccessMessage] = useState(''); // Stocke le message de succès
  const [loading, setLoading] = useState(false); // Gère l'état du chargement

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prevData) => ({
      ...prevData,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setSuccessMessage('If this email address exists, you will receive the password reset instructions'); // Réinitialise le message de succès

    try {
      const response = await resetPassword(formData);
      if (response.message) {
        setSuccessMessage(response.message); // Définit le message de succès depuis la réponse
      }
    } catch (error) {
      console.error('An error occurred during password reset:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <Form onSubmit={handleSubmit}>
        <Form.Label>Please submit your email to reset your password</Form.Label>
        <Form.Control
          type="email"
          placeholder="Enter your email"
          name="email"
          value={formData.email}
          onChange={handleChange}
          required
        />
        <Button type="submit" disabled={loading}>
          {loading ? 'Submitting...' : 'Reset my password'}
        </Button>
      </Form>

      {/* Affichage du message de succès */}
      {successMessage && (
        <Alert variant="success" className="mt-3">
          {successMessage}
        </Alert>
      )}
    </div>
  );
}
