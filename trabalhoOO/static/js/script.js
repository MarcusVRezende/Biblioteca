document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".btn").forEach(button => {
        button.addEventListener("click", function (event) {
            event.preventDefault(); // Impede redirecionamento imediato

            const url = this.getAttribute("href"); // Obtém a URL do botão

            // Exibe um alerta de confirmação antes de prosseguir
            if (!confirm("Tem certeza que deseja realizar esta ação?")) {
                return; // Cancela a ação se o usuário não confirmar
            }

            // Desativa apenas o botão clicado e adiciona o estado de carregamento
            this.disabled = true;
            this.classList.add("loading");
            this.innerHTML = "🔄 Processando...";

            // Após 1 segundo, redireciona e reativa o botão
            setTimeout(() => {
                window.location.href = url;
                this.disabled = false;
                this.classList.remove("loading");
                this.innerHTML = "✔ Concluído";
            }, 1000);
        });
    });
});
