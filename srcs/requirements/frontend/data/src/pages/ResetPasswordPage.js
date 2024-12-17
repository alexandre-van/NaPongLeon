/*
import { Form, Button, Container, Alert } from 'react-bootstrap';
import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api.js';

export default function ResetPasswordPage() {
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [success, setSuccess] = useState(false);
    const [error, setError] = useState('');
    const { uid, token } = useParams();
    const navigate = useNavigate();

    useEffect(() => {
        // Log détaillé des paramètres
        console.log('Paramètres reçus:', {
            uid: uid,
            token: token,
            // Décodage de l'uid pour vérification
            decodedUid: uid ? atob(uid) : 'non défini'
        });

        // Vérification de la présence des paramètres
        if (!uid || !token) {
            console.error('Paramètres manquants:', { uid, token });
            setError('Lien de réinitialisation invalide');
            // Attendre un peu avant de rediriger
            setTimeout(() => navigate('/login'), 3000);
            return;
        }
    }, [uid, token, navigate]);

    const handleSubmit = (e) => {
        e.preventDefault();
        console.log('Tentative de réinitialisation avec uid:', uid);

        if (password !== confirmPassword) {
            setError('Passwords do not match');
            return ;
        }

        try {
            const response = api.post(`/authentication/users/password-reset-confirmation/${uid}/${token}/`, {
                new_password: password
            });
            if (response.data && response.data.message !== 'Password modified') {
                const errorMessages = response.data.errors;
                setError(Array.isArray(errorMessages) ? errorMessages.join(', ') : errorMessages);
                return;
            }

            setSuccess(true);
            setTimeout(() => {
                navigate('/login');
            }, 3000);
        } catch (err) {
            setError(err.response?.data?.message || 'An error occured');
        }
    }

    if (success) {
        return (
            <Container>
                <Alert variant="success">
                    Password successfully reset, redirecting to login...
                </Alert>
            </Container>
        );
    }

    return (
        <Container>
            {error && <Alert variant="danger">{error}</Alert>}
            <Form onSubmit={handleSubmit}>
                <Form.Group>
                    <Form.Label>New password</Form.Label>
                    <Form.Control
                        type="password"
                        placeholder="Enter your new password"
                        name="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />
                </Form.Group>
                <Form.Group>
                    <Form.Label>Retype new password</Form.Label>
                    <Form.Control
                        type="password"
                        placeholder="Retype your new password"
                        name="retype-password"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        required
                    />
                </Form.Group>

                <Button type="submit">Reset password</Button>
            </Form>
        </Container>
    );
}
*/
import { Form, Button, Container, Alert } from 'react-bootstrap';
import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api.js';

export default function ResetPasswordPage() {
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [success, setSuccess] = useState(false);
    const [error, setError] = useState('');
    const { uid, token } = useParams();
    const navigate = useNavigate();

    useEffect(() => {
        // Vérification des paramètres uniquement au chargement initial
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

            console.log("Server response:", response.data);
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
                    Go to Login page
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
        </Container>
    );
}