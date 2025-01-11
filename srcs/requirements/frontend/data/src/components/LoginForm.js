import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Button, Form } from 'react-bootstrap'; // Importation de React-Bootstrap
import { useUser } from '../contexts/UserContext.js';

const LoginForm = ({ onLogin, error }) => { // Ajout de la prop `error`
  const [formData, setFormData] = useState({
    username: '',
    password: '',
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prevData) => ({
      ...prevData,
      [name]: value,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onLogin(formData);
  };

  return (
    <div>
      <h1 className="title">LOGIN</h1>
      <div className="BorderBox">
        <Form onSubmit={handleSubmit}>
          <Form.Group controlId="formBasicUsername">
            <Form.Label>Username</Form.Label>
            <Form.Control
              type="text"
              placeholder="Enter your username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              required
            />
          </Form.Group>

          <Form.Group controlId="formBasicPassword">
            <Form.Label>Password</Form.Label>
            <Form.Control
              type="password"
              placeholder="Enter your password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
            />
          </Form.Group>

          {/* Affichage du message d'erreur en rouge sous le formulaire */}
          {error && <p className="error-message">{error}</p>}

          <Button className="options" variant="primary" type="submit">
            LOG IN
          </Button>
          <Button className="options" variant="secondary" onClick={useUser().login42}>
            LOG IN WITH 42
          </Button>

          <div className="mt-3">
            <Link to="/register">Don't have an account? Register</Link>
            <br />
            <Link to="/forgot-password">Forgot Password?</Link>
          </div>
        </Form>
      </div>
    </div>
  );
};

export default LoginForm;
