import { useUser } from '../contexts/UserContext.js';
import { useNavigate } from 'react-router-dom';

const OAuth42Button = () => {
    const { OAuthLoginVia42 } = useUser();
    const navigate = useNavigate();

    const handleLoginVia42 = async () => {
        try {
            const response = await OAuthLoginVia42();
            if (response.data && response.data.message !== 'Login successful') {
                throw new Error("Login via 42 failed")
            }
            navigate('/');
        } catch (error) {
            console.log(error.message);
        }
    };

    return (
        <button onClick={handleLoginVia42}>
            Login via 42
        </button>
    );
};

export default OAuth42Button;