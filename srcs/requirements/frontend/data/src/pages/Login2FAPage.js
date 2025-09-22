import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Button, Form } from 'react-bootstrap';
import { useUser } from '../contexts/UserContext.js';
import api from '../services/api.js';

export default function Login2FAPage() {
    const [code, setCode] = useState('');
    const [error, setError] = useState(false);
    const [errorMessage, setErrorMessage] = useState('');
    const { checkAuth, isAuthenticated } = useUser();
    const navigate = useNavigate();

    const urlParams = new URLSearchParams(window.location.search);
    const tempToken = urlParams.get('token');

    const handleSubmit = async (e) => {
        e.preventDefault();

        try {
            const response = await api.post('/authentication/auth/login/2fa/', {
                code: code,
                temp_token: tempToken
            });
            if (response.data.message !== 'Login successful') {
                setError(true);
                setErrorMessage('Failed 2FA verification');
            }
            else {
                setError(false);
                setErrorMessage('');
                await checkAuth();
                navigate('/');
            }
        } catch (error) {
            console.log('Error:', error);
        }
    };

    useEffect(() => {
        if (isAuthenticated) {
          navigate('/');
        }
      }, [isAuthenticated, navigate]);

    return (
        <div>
            {error && <div>{errorMessage}</div>}
            <Form onSubmit={handleSubmit}>
                <Form.Label>Please submit your 2FA code to login</Form.Label>
                <Form.Control
                    type="text"
                    name="2FACode"
                    value={code}
                    onChange={(e) => setCode(e.target.value)}
                />
            
                <Button type="submit">
                    Submit 2FA code
                </Button>
            </Form>
            <Link to="/login">
                Go back to login page
            </Link>
        </div>
    );
}