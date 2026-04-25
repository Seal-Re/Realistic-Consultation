<template>
  <div id="app">
    <canvas id="canvas"></canvas>
    <div id="chat-container">
      <div id="chat-history">
        <div
          v-for="(message, index) in chatMessages"
          :key="index"
          :class="['chat-message', message.sender === '你'? 'user-message' : 'ai-message']"
        >
          <strong>{{ message.sender }}:</strong>
          <span v-html="message.content"></span>
        </div>
      </div>
      <input v-model="inputText" type="text" id="chat-input" placeholder="输入你的消息" />
      <button @click="sendMessage" id="send-button">发送</button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import axios from 'axios';
import '@/js/live2dcubismcore.min.js';
import '@/js/live2d.min.js';
import '@/js/pixi.min.js';
import '@/js/cubism4.min.js';
import '@/js/jquery-3.1.1.min.js';

// 数字人模型
const cubism4Model = "./assets/Doro/Doro.model3.json";

const inputText = ref('');
const chatMessages = ref([]);

const initLive2D = async () => {
  const app = new PIXI.Application({
    view: document.getElementById("canvas"),
    autoStart: true,
    resizeTo: window,
    backgroundColor: 0x333333
  });

  const models = await Promise.all([
    live2d.Live2DModel.from(cubism4Model)
  ]);

  models.forEach((model) => {
    app.stage.addChild(model);

    const scaleX = (window.innerWidth) / model.width;
    const scaleY = (window.innerHeight) / model.height;

    // fit the window
    model.scale.set(Math.min(scaleX, scaleY));
    model.y = window.innerHeight * 0.1;
    draggable(model);
  });

  const model4 = models[0];
  model4.x = (window.innerWidth * 0.1);

  model4.on("hit", (hitAreas) => {
    if (hitAreas.includes("Body")) {
      model4.motion("Tap");
    }

    if (hitAreas.includes("Head")) {
      model4.expression();
    }
  });

  const talk = (model, audio) => {
    var audio_link = audio;
    var volume = 1;
    var expression = 8;
    var resetExpression = true;
    var crossOrigin = "anonymous";

    model.speak(audio_link, {
      volume: volume,
      expression: expression,
      resetExpression: resetExpression,
      crossOrigin: crossOrigin
    });
    model.speak(audio_link);
    model.speak(audio_link, { volume: volume });
    model.speak(audio_link, { expression: expression, resetExpression: resetExpression });
  };

  const sendMessage = async () => {
    if (inputText.value.trim() === "") {
      return;
    }
    chatMessages.value.push({ sender: '你', content: inputText.value });
    try {
      const response = await axios.post("http://127.0.0.1:2020/api/AI", {
        question: inputText.value
      });
      let aiResponse = response.data.message;
      let originalAiResponse = aiResponse;
      aiResponse = aiResponse.replace(/\n/g, '<br>');
      chatMessages.value.push({ sender: 'AI', content: aiResponse });

      const audioResponse = await axios.get(`http://127.0.0.1:2020/dealAudio?file_name=test.mp3&voice=xiaoxiao&text=${encodeURIComponent(originalAiResponse)}`);
      const audioUrl = audioResponse.data + "?v=" + new Date().getTime();
      talk(model4, audioUrl);
    } catch (error) {
      console.error('请求AI接口失败:', error);
      chatMessages.value.push({ sender: 'AI', content: '很抱歉，无法获取回答。' });
    }
    inputText.value = '';
  };

  const draggable = (model) => {
    model.buttonMode = true;
    model.on("pointerdown", (e) => {
      model.dragging = true;
      model._pointerX = e.data.global.x - model.x;
      model._pointerY = e.data.global.y - model.y;
    });
    model.on("pointermove", (e) => {
      if (model.dragging) {
        model.position.x = e.data.global.x - model._pointerX;
        model.position.y = e.data.global.y - model._pointerY;
      }
    });
    model.on("pointerupoutside", () => (model.dragging = false));
    model.on("pointerup", () => (model.dragging = false));
  };

  initLive2D();
}
</script>

<style scoped>
#app {
  display: flex;
  justify-content: space-between;
}

#canvas {
  width: 50%;
}

#chat-container {
  width: 40%;
  position: relative;
  top: 50px;
  right: 50px;
  color: #ffffff;
  font-size: 18px;
}

#chat-history {
  height: 400px;
  overflow-y: auto;
  border: 1px solid #ccc;
  padding: 10px;
  margin-bottom: 10px;
  display: flex;
  flex-direction: column;
}

#chat-input {
  width: 100%;
  height: 30px;
}

#send-button {
  margin-top: 10px;
}

.label {
  font-size: 32px;
  font-weight: 800;
}

.chat-message {
  margin-bottom: 10px;
  padding: 10px;
  border-radius: 10px;
  max-width: 80%;
  clear: both;
}

.user-message {
  background-color: #007BFF;
  color: white;
  align-self: flex-end;
}

.ai-message {
  background-color: #6c757d;
  color: white;
  align-self: flex-start;
}
</style>    