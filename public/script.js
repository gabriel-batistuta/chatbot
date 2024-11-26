const chatBox = document.getElementById('chat-box');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const conversationList = document.getElementById('conversation-list');
const newConversationBtn = document.getElementById('new-conversation-btn');

let currentConversation = []; // Armazena a conversa atual
let currentConversationIndex = -1; // Índice da conversa ativa
let conversationHistory = []; // Histórico de conversas

// URL do backend
const BACKEND_URL = "http://127.0.0.1:8000/chatbot/text/";

// Função para enviar a mensagem
// Função para enviar a mensagem
async function sendMessage() {
  const userMessage = userInput.value.trim();

  if (userMessage !== '') {
    addMessage(userMessage, 'user');
    currentConversation.push({ sender: 'user', message: userMessage });
    userInput.value = '';
    console.log(userMessage);

    try {
      const botResponse = await fetchBotResponseStream(userMessage);
      console.log(botResponse);
      saveConversation(); // Salva a conversa no histórico
    } catch (error) {
      console.error("Erro ao se comunicar com o backend:", error);
      addMessage("Desculpe, houve um erro ao processar sua mensagem.", 'bot');
    }
  }
}

// Função para obter a resposta do backend com stream
async function fetchBotResponseStream(message) {
  const formData = new FormData();
  formData.append("text", message);

  // Faz a requisição ao backend
  const response = await fetch(BACKEND_URL, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`Erro ao se conectar ao backend: ${response.statusText}`);
  }

  // Lê o corpo do stream
  const reader = response.body.getReader();
  const decoder = new TextDecoder("utf-8");
  let botResponse = ""; // Acumula a resposta completa
  const botMessageElement = addMessage("", "bot"); // Adiciona o elemento para exibir o texto

  // Processa os chunks recebidos
  while (true) {
    const { value, done } = await reader.read();
    if (done) break; // Se o stream terminou, sai do loop

    const chunk = decoder.decode(value, { stream: true }); // Decodifica o chunk
    console.log("Chunk recebido no frontend:", chunk);
    botResponse += chunk; // Acumula o texto completo
    botMessageElement.innerHTML = `<p>${botResponse}</p>`; // Atualiza o texto no chat em tempo real
    chatBox.scrollTop = chatBox.scrollHeight; // Rola o chat para o fim
  }

  return botResponse; // Retorna a resposta completa
}

// Função para adicionar uma nova mensagem ao chat
function addMessage(message, sender) {
  const messageElement = document.createElement("div");
  messageElement.classList.add("message", sender);
  messageElement.innerHTML = `<p>${message}</p>`;
  chatBox.appendChild(messageElement);
  chatBox.scrollTop = chatBox.scrollHeight;
  return messageElement; // Retorna o elemento para atualizações dinâmicas
}

// Envia mensagem ao clicar no botão
sendBtn.addEventListener('click', sendMessage);

// Envia mensagem ao pressionar Enter
userInput.addEventListener('keydown', (event) => {
  if (event.key === 'Enter') {
    sendMessage();
  }
});

// // Função para adicionar uma nova mensagem na caixa de chat
// function addMessage(message, sender) {
//   const messageElement = document.createElement('div');
//   messageElement.classList.add('message', sender);
//   messageElement.innerHTML = `<p>${message}</p>`;
//   chatBox.appendChild(messageElement);
//   chatBox.scrollTop = chatBox.scrollHeight;
// }

// Função para salvar a conversa na barra lateral
function saveConversation() {
  const conversationName = `Conversa ${conversationHistory.length + 1}`;

  // Cria um novo item de conversa
  const conversationItem = document.createElement('div');
  conversationItem.classList.add('conversation-item');
  conversationItem.id = `conversation-${conversationHistory.length}`;

  const conversationSelectorContainer = document.createElement('div');
  conversationSelectorContainer.classList.add('conversation-selector-container');

  // Botão que representa a conversa
  const conversationSelector = document.createElement('button');
  conversationSelector.textContent = conversationName;
  conversationSelector.classList.add('conversation-selector');
  const conversationIndex = conversationHistory.length;

  conversationSelector.addEventListener('click', () => loadConversation(conversationIndex));

  // Botão de opções (três pontos)
  const optionsButton = document.createElement('button');
  optionsButton.classList.add('options-button');
  optionsButton.innerHTML = '&#x22EE;'; // Três pontos verticais

  // Menu popup de opções
  const optionsMenu = document.createElement('div');
  optionsMenu.classList.add('options-menu');
  optionsMenu.style.display = 'none'; // Oculto por padrão
  optionsMenu.innerHTML = `
    <button class="menu-item rename">Renomear</button>
    <button class="menu-item share">Compartilhar</button>
    <button class="menu-item delete">Excluir</button>
  `;

  // Mostrar/ocultar menu ao clicar no botão de opções
  optionsButton.addEventListener('click', () => {
    optionsMenu.style.display = optionsMenu.style.display === 'block' ? 'none' : 'block';
  });

  // Fechar o menu ao clicar fora
  document.addEventListener('click', (event) => {
    if (!conversationSelectorContainer.contains(event.target)) {
      optionsMenu.style.display = 'none';
    }
  });

  // Função para renomear a conversa
  optionsMenu.querySelector('.rename').addEventListener('click', () => {
    const newName = prompt('Digite o novo nome da conversa:', conversationName);
    if (newName) {
      conversationSelector.textContent = newName;
    }
    optionsMenu.style.display = 'none';
  });

  // Função para compartilhar a conversa
  optionsMenu.querySelector('.share').addEventListener('click', () => {
    alert(`Compartilhando a conversa: ${conversationName}`);
    optionsMenu.style.display = 'none';
  });

  // Função para excluir a conversa
  optionsMenu.querySelector('.delete').addEventListener('click', () => {
    if (confirm('Tem certeza de que deseja excluir esta conversa?')) {
      // Remove do DOM
      conversationItem.remove();

      // Remove do histórico
      conversationHistory.splice(conversationIndex, 1);

      // Se a conversa excluída for a conversa ativa
      if (currentConversationIndex === conversationIndex) {
        chatBox.innerHTML = ''; // Limpa o chat
        currentConversation = []; // Limpa a conversa ativa
        currentConversationIndex = -1; // Reseta o índice da conversa ativa
        alert("A conversa ativa foi excluída.");
      }

      // Atualiza os índices das conversas restantes no DOM
      const remainingConversations = document.querySelectorAll('.conversation-item');
      remainingConversations.forEach((item, newIndex) => {
        item.id = `conversation-${newIndex}`;
        item.querySelector('.conversation-selector').addEventListener('click', () => loadConversation(newIndex));
      });
    }
    optionsMenu.style.display = 'none';
  });

  // Monta a estrutura do item de conversa
  conversationSelectorContainer.appendChild(conversationSelector);
  conversationSelectorContainer.appendChild(optionsButton);
  conversationItem.appendChild(conversationSelectorContainer);
  conversationItem.appendChild(optionsMenu);

  conversationList.appendChild(conversationItem);

  // Salva a conversa no histórico
  conversationHistory.push(currentConversation);
  currentConversationIndex = conversationHistory.length - 1;
}

// Função para carregar uma conversa salva na barra lateral
function loadConversation(index) {
  chatBox.innerHTML = ''; // Limpa o chat atual
  const conversation = conversationHistory[index];
  
  // Adiciona as mensagens da conversa salva
  conversation.forEach((message) => {
    addMessage(message.message, message.sender);
  });

  // Atualiza o índice da conversa ativa
  currentConversationIndex = index;
}

// Função para iniciar uma nova conversa
newConversationBtn.addEventListener('click', () => {
  currentConversationIndex = -1;
  currentConversation = [];
  chatBox.innerHTML = ''; // Limpa a caixa de chat
});
