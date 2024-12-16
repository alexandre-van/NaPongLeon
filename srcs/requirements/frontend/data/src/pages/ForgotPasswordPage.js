import { useState } from 'react';
import { Button, Form } from 'react-bootstrap';
import { useUser } from '../contexts/UserContext.js';

export default function ForcedPasswordPage() {
    const [formData, setFormData] = useState({
        email: '',
    });
    const { resetPassword } = useUser();

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prevData => ({
            ...prevData,
            [name]: value,
        }));
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        resetPassword(formData);
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
                <Button type="submit">Reset my password</Button>
            </Form>


        </div>
    );
}