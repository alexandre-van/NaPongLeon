import api from "../services/api.js";

const useUserInfo = () => {
  const getUserInfo = async () => {
    const success = await api.get('/authentication/get-self-info/');
    if (success) {

    }
  };

  return { getUserInfo };
};

export default useUserInfo;
