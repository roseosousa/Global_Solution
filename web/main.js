const api = path => `/api/${path}`

const $ = sel => document.querySelector(sel)

const loginSection = $('#login')
const panel = $('#panel')
const userLabel = $('#userLabel')
const output = $('#output')
const btnLogout = $('#btnLogout')

let currentUser = JSON.parse(localStorage.getItem('user') || 'null')
let token = localStorage.getItem('token') || null

function setToken(t, user){
  token = t
  if(t) localStorage.setItem('token', t)
  else localStorage.removeItem('token')
  if(user) localStorage.setItem('user', JSON.stringify(user))
  else localStorage.removeItem('user')
}

function authHeaders(h){
  h = h || {}
  if(token) h['Authorization'] = `Bearer ${token}`
  return h
}

async function authFetch(path, opts={}){
  const url = path.startsWith('/api/') ? path : api(path)
  opts.headers = Object.assign({'Content-Type':'application/json'}, opts.headers || {}, authHeaders())
  return fetch(url, opts)
}

function showPanel(){
  if(currentUser){
    userLabel.innerText = `Olá, ${currentUser.nome} — ${currentUser.cargo || ''}`
    loginSection.classList.add('hidden')
    panel.classList.remove('hidden')
  }
}

function logout(){
  setToken(null, null)
  currentUser = null
  userLabel.innerText = ''
  panel.classList.add('hidden')
  loginSection.classList.remove('hidden')
  appendOut('Desconectado.')
}

// Init UI if already logged
if(token && localStorage.getItem('user')){
  currentUser = JSON.parse(localStorage.getItem('user'))
  showPanel()
}

$('#btnLogin').addEventListener('click', async () => {
  const nome = $('#nome').value.trim()
  const senha = $('#senha').value
  if(!nome){alert('Digite seu nome');return}
  const res = await fetch(api('login'),{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({nome,senha})})
  const j = await res.json()
  if(j.ok){
    currentUser = j.user
    setToken(j.token, j.user)
    showPanel()
    appendOut('Login efetuado')
  } else {
    appendOut('Login falhou: '+(j.error||'erro'))
  }
})

btnLogout && btnLogout.addEventListener('click', () => logout())

$('#btnSeed').addEventListener('click', async () => {
  appendOut('Executando seed...')
  const res = await authFetch('seed',{method:'POST'})
  const j = await res.json()
  appendOut(JSON.stringify(j))
})

$('#btnGen').addEventListener('click', async () => {
  appendOut('Gerando proposta...')
  const payload = {id_cliente:1,valor:19990,id_responsavel: currentUser ? currentUser.id : 1}
  const res = await authFetch('generate_proposal',{method:'POST',body:JSON.stringify(payload)})
  const j = await res.json()
  appendOut(JSON.stringify(j))
})

$('#btnWell').addEventListener('click', async () => {
  appendOut('Registrando wellbeing...')
  const payload = {id_funcionario: currentUser ? currentUser.id : 1, problema: 'estresse demo'}
  const res = await authFetch('register_wellbeing',{method:'POST',body:JSON.stringify(payload)})
  const j = await res.json()
  appendOut(JSON.stringify(j))
})

$('#btnReport').addEventListener('click', async () => {
  appendOut('Gerando relatório...')
  const res = await authFetch('run_report',{method:'POST'})
  const j = await res.json()
  appendOut(JSON.stringify(j))
})

$('#btnList').addEventListener('click', async () => {
  appendOut('Listando deliverables...')
  const res = await authFetch('deliverables',{method:'GET'})
  const j = await res.json()
  if(j.ok){
    appendOut('Arquivos: ' + j.files.join(', '))
    output.prepend(document.createElement('div'))
    const container = document.createElement('div')
    j.files.forEach(f => {
      const row = document.createElement('div')
      row.innerHTML = `<span>${f}</span> <button class="btn" data-file="${f}">Baixar</button>`
      const btn = row.querySelector('button')
      btn.addEventListener('click', () => downloadFile(f))
      container.appendChild(row)
    })
    output.prepend(container)
  } else appendOut('Erro: '+(j.error||''))
})

async function downloadFile(filename){
  appendOut('Preparando download: '+filename)
  const res = await fetch(`/deliverables/${encodeURIComponent(filename)}`,{headers:authHeaders()})
  if(!res.ok){ appendOut('Erro ao baixar: '+res.status); return }
  const blob = await res.blob()
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(url)
}

function appendOut(text){
  const d = document.createElement('div')
  d.innerHTML = `<pre style="white-space:pre-wrap">${text}</pre>`
  output.prepend(d)
}
