const { createApp } = Vue;

const URGENCY_ALPHA = 1.5;
const URGENCY_BETA = 0.10;

function urgencyCoefficient(days) {
    if (days < 1) return 1;
    return 1 + URGENCY_ALPHA * Math.exp(-URGENCY_BETA * (days - 1));
}

function calculatePrice(basePrice, techMultiplier, days, volume) {
    const urgency = urgencyCoefficient(days);
    const raw = basePrice * volume * techMultiplier * urgency;
    return Math.round(raw * 100) / 100;
}

createApp({
    data() {
        return {
            services: [],
            selectedServiceId: null,
            selectedTechId: null,
            deadlineDays: 14,
            volume: 3,
            loading: true,
            error: null,
            showModal: false,
            form: { clientName: '', clientContact: '', comment: '' },
            submitting: false,
            submitResult: null,
            submitErrors: [],
        };
    },
    computed: {
        selectedService() {
            return this.services.find(s => s.id === this.selectedServiceId) || null;
        },
        availableTechnologies() {
            return this.selectedService ? this.selectedService.technologies : [];
        },
        selectedTechnology() {
            if (!this.selectedTechId) return null;
            return this.availableTechnologies.find(t => t.id === this.selectedTechId) || null;
        },
        price() {
            if (!this.selectedService || !this.selectedTechnology) return null;
            return calculatePrice(
                this.selectedService.base_price,
                this.selectedTechnology.multiplier,
                this.deadlineDays,
                this.volume,
            );
        },
        urgency() {
            return urgencyCoefficient(this.deadlineDays);
        },
    },
    watch: {
        selectedServiceId() {
            if (this.availableTechnologies.length > 0) {
                this.selectedTechId = this.availableTechnologies[0].id;
            } else {
                this.selectedTechId = null;
            }
        },
    },
    async mounted() {
        try {
            const resp = await fetch('/api/services');
            if (!resp.ok) throw new Error('Помилка сервера');
            this.services = await resp.json();
            if (this.services.length > 0) {
                this.selectedServiceId = this.services[0].id;
            }
        } catch (e) {
            this.error = 'Не вдалося завантажити список послуг';
        } finally {
            this.loading = false;
        }
    },
    methods: {
        openModal() {
            this.submitResult = null;
            this.submitErrors = [];
            this.showModal = true;
        },
        closeModal() {
            this.showModal = false;
        },
        async submitRequest() {
            this.submitting = true;
            this.submitErrors = [];
            const payload = {
                client_name: this.form.clientName,
                client_contact: this.form.clientContact,
                service_id: this.selectedServiceId,
                technology_id: this.selectedTechId,
                deadline_days: this.deadlineDays,
                volume: this.volume,
                comment: this.form.comment,
            };
            try {
                const resp = await fetch('/api/requests', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload),
                });
                const data = await resp.json();
                if (resp.ok) {
                    this.submitResult = {
                        message: `Дякуємо! Заявку №${data.request_id} прийнято. Орієнтовна вартість: ${this.formatMoney(data.calculated_price)} ₴`,
                    };
                    this.form = { clientName: '', clientContact: '', comment: '' };
                } else {
                    this.submitErrors = data.errors || [data.error || 'Помилка сервера'];
                }
            } catch (e) {
                this.submitErrors = ["Помилка з'єднання з сервером"];
            } finally {
                this.submitting = false;
            }
        },
        formatMoney(value) {
            if (value === null || value === undefined) return '—';
            return Number(value).toLocaleString('uk-UA', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
        },
    },
}).mount('#calculator-app');
