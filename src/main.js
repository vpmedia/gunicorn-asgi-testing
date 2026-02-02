const button = document.querySelector('#load')
const output = document.querySelector('#output')

button.addEventListener('click', async () => {
  output.textContent = 'Loading...'

  try {
    const res = await fetch('/api')
    if (!res.ok) throw new Error('Network response was not ok')

    const data = await res.json()
    output.textContent = JSON.stringify(data, null, 2)
  } catch (err) {
    output.textContent = `Error: ${err.message}`
  }
})