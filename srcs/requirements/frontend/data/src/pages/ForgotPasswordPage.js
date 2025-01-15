import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Button, Form, Alert } from 'react-bootstrap';
import { useUser } from '../contexts/UserContext.js';
import { useNavigate } from 'react-router-dom';

export default function ForcedPasswordPage() {
  const { resetPassword, isAuthenticated, user } = useUser();
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: '',
  });
  const [successMessage, setSuccessMessage] = useState('');
  const [loading, setLoading] = useState(false);

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
    setSuccessMessage(''); // Réinitialise le message de succès

    const email = isAuthenticated ? user?.email : formData.email;

    try {
      const response = await resetPassword({ email });
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
      {isAuthenticated ? (
        <>
          <p>
            Email: <strong>{user.email}</strong>
          </p>
          <Button onClick={handleSubmit} disabled={loading}>
            {loading ? 'Sending email...' : 'Send reset email'}
          </Button>
        </>
      ) : (
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
  
          {/* Afficher le lien uniquement si l'utilisateur n'est pas authentifié */}
          <Link to="/login" className="d-block mt-3">
            Go back to login page
          </Link>
        </Form>
      )}
  
      {/* Affichage du message de succès */}
      {successMessage && (
        <Alert variant="success" className="mt-3">
          {successMessage}
        </Alert>
      )}
    </div>
  );
}  
