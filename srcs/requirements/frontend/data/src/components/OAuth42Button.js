import { useUser } from '../contexts/UserContext.js';

const OAuth42Button = () => {
    const { OAuthLoginVia42 } = useUser();

    const handleLoginVia42 = async () => {
        try {
            const response = await OAuthLoginVia42();

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