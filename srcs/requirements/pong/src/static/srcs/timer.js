
const startTime = Date.now();

function getTimer() {
      const elapsedTime = Date.now() - startTime;
      return elapsedTime;
}
  
export { getTimer };