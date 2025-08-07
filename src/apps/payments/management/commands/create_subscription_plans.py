"""
Management command to create subscription plans
"""
from django.conf import settings
from django.core.management.base import BaseCommand

from ...infrastructure.models import SubscriptionPlanModel


class Command(BaseCommand):
    help = "Crea planes de suscripción predeterminados"

    def add_arguments(self, parser):
        parser.add_argument(
            "--update", action="store_true", help="Actualizar planes existentes"
        )

    def handle(self, *args, **options):
        """Crear planes de suscripción"""
        plans_data = [
            {
                "name": "Premium Mensual",
                "description": "Acceso premium con facturación mensual",
                "price": 999,  # 9.99 EUR en centavos
                "currency": "EUR",
                "interval": "month",
                "interval_count": 1,
                "features": [
                    "Música sin anuncios",
                    "Descargas offline",
                    "Calidad de audio premium",
                    "Saltos ilimitados",
                    "Acceso a podcasts exclusivos",
                ],
                "stripe_price_id": settings.STRIPE_PREMIUM_MONTHLY_PRICE_ID,
            },
            {
                "name": "Premium Anual",
                "description": "Acceso premium con facturación anual (ahorra 20%)",
                "price": 9999,  # 99.99 EUR en centavos (ahorro de 20%)
                "currency": "EUR",
                "interval": "year",
                "interval_count": 1,
                "features": [
                    "Música sin anuncios",
                    "Descargas offline",
                    "Calidad de audio premium",
                    "Saltos ilimitados",
                    "Acceso a podcasts exclusivos",
                    "Ahorro del 20% vs plan mensual",
                ],
                "stripe_price_id": settings.STRIPE_PREMIUM_YEARLY_PRICE_ID,
            },
        ]

        for plan_data in plans_data:
            if not plan_data["stripe_price_id"]:
                self.stdout.write(
                    self.style.WARNING(
                        f'⚠️ Saltando {plan_data["name"]}: STRIPE_PRICE_ID no configurado'
                    )
                )
                continue

            plan, created = SubscriptionPlanModel.objects.get_or_create(
                stripe_price_id=plan_data["stripe_price_id"], defaults=plan_data
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"✅ Plan creado: {plan.name}"))
            elif options["update"]:
                # Actualizar plan existente
                for field, value in plan_data.items():
                    setattr(plan, field, value)
                plan.save()
                self.stdout.write(
                    self.style.SUCCESS(f"🔄 Plan actualizado: {plan.name}")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"⚠️ Plan ya existe: {plan.name} (usa --update para actualizar)"
                    )
                )

        self.stdout.write(self.style.SUCCESS("\n🎉 Proceso completado!"))

        # Mostrar instrucciones
        self.stdout.write("\n📋 Próximos pasos:")
        self.stdout.write(
            "1. Configura tus Price IDs de Stripe en las variables de entorno"
        )
        self.stdout.write("2. Ejecuta las migraciones: python manage.py migrate")
        self.stdout.write("3. Ejecuta este comando nuevamente con --update")
        self.stdout.write("4. Configura los webhooks en Stripe Dashboard")
