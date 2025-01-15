
import { Form, Button, Container, Alert } from 'react-bootstrap';
import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import api from '../services/api.js';
import { useUser } from '../contexts/UserContext.js';

export default function ResetPasswordPage() {
    const { user, isAuthenticated } = useUser();
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [success, setSuccess] = useState(false);
    const [error, setError] = useState('');
    const { uid, token } = useParams();
    const navigate = useNavigate();

    useEffect(() => {
        if (!uid || !token) {
            setError('Invalid Reset Password link');
        }
    }, [uid, token]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        if (password !== confirmPassword) {
            setError('Passwords do not match');
            return;
        }

        try {
            const response = await api.post(
                `/authentication/users/password-reset-confirmation/${uid}/${token}/`, 
                { new_password: password }
            );
            setSuccess(true);

        } catch (error) {
            console.log("Error:", error);
            
            if (error.response) {
                const responseData = error.response.data;
                
                if (responseData.errors) {
                    const errorMessage = Array.isArray(responseData.errors) 
                        ? responseData.errors.join('\n')
                        : responseData.errors;
                    setError(errorMessage);
                } else if (responseData.error) {
                    setError(responseData.error);
                } else {
                    setError('Error when resetting password');
                }
            } else {
                setError('Impossible to connect with the server');
            }
        }
    };

    if (success) {
        return (
            <Container>
                <Alert variant="success">
                    Password has been modified
                </Alert>
                <Button onClick={() => navigate('/login')}>
                    Go to {isAuthenticated ? "home": "login"} page
                </Button>
            </Container>
        );
    }

    return (
        <Container className="mt-5">
            {error && <Alert variant="danger">{error}</Alert>}
            <Form onSubmit={handleSubmit}>
                <Form.Group className="mb-3">
                    <Form.Label>New password</Form.Label>
                    <Form.Control
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />
                    <Form.Text className="text-muted">
                        <p>Your password must contain:</p>
                        <ul>
                            <li>At least 10 characters</li>
                            <li>At least an uppercase character</li>
                            <li>At least a special character (!@#$%^&*(),.?":{}|{'<>'})</li>
                        </ul>
                    </Form.Text>
                </Form.Group>

                <Form.Group className="mb-3">
                    <Form.Label>Retype Password</Form.Label>
                    <Form.Control
                        type="password"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        required
                    />
                </Form.Group>

                <Button type="submit" variant="primary">
                    Reset password
                </Button>

            </Form>
            <Link to="/login">
                Go back to {isAuthenticated ? "home": "login"} page
            </Link>
        </Container>
    );
}