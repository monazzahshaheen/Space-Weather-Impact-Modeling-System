export async function fetchTLE() {
  const response = await fetch(
    "https://celestrak.org/NORAD/elements/stations.txt"
  )
  const text = await response.text()
  return text
}
export function parseTLE(text) {
  const lines = text.split("\n")
  const satellites = []

  for (let i = 0; i < lines.length; i += 3) {
    satellites.push({
      name: lines[i],
      line1: lines[i + 1],
      line2: lines[i + 2],
    })
  }
  return satellites
}
