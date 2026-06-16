import discord
from discord.ext import commands
from discord.ui import Button, View, Select

# ===== KONFIG =====
TOKEN = "MTUxNTA1MDYxNDc5MzY5OTQ0OA.GWLOkE.yMcdKBTI26N9ly428gA-nLPoQlFXKGQvTk2Hzs"

VERIFY_ROLE_ID = 1510555413517439089
VERIFY_CHANNEL_ID = 1512111819987091547
# ==================

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Zalogowano jako {bot.user}")

# ===== WERYFIKACJA =====
@bot.command()
async def setup_verify(ctx):
    channel = bot.get_channel(VERIFY_CHANNEL_ID)
    if channel is None:
        await ctx.send("Nie moge znalezc kanalu weryfikacji.")
        return

    # Embed (ramka)
    embed = discord.Embed(
        title="WERYFIKACJA",
        description="Kliknij przycisk ponizej, aby sie zweryfikowac.",
        color=discord.Color.green()
    )

    # Przycisk
    button = Button(label="Zweryfikuj sie", style=discord.ButtonStyle.green)

    async def button_callback(interaction):
        role = interaction.guild.get_role(VERIFY_ROLE_ID)
        if role is None:
            await interaction.response.send_message("Nie moge znalezc roli.", ephemeral=True)
            return

        # Sprawdzenie czy user juz ma role
        if role in interaction.user.roles:
            await interaction.response.send_message("Juz jestes zweryfikowany.", ephemeral=True)
            return

        # Nadanie roli
        await interaction.user.add_roles(role)
        await interaction.response.send_message("Zostales zweryfikowany!", ephemeral=True)

    button.callback = button_callback

    view = View()
    view.add_item(button)

    # Wyslanie embeda z przyciskiem
    await channel.send(embed=embed, view=view)

# ===== TICKETY =====

import asyncio

TICKET_CATEGORY_ID = 1515064637912125511  # <-- ID KATEGORII

# ===== SELECT KATEGORII =====

class TicketSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Zglos cheatera"),
            discord.SelectOption(label="Backup"),
            discord.SelectOption(label="Znalazlem blad"),
            discord.SelectOption(label="Zakup paysafecard"),
            discord.SelectOption(label="Inne"),
        ]

        super().__init__(
            placeholder="Wybierz kategorie zgloszenia",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="ticket_select"  # <-- MUSI BYC
        )

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        category = guild.get_channel(TICKET_CATEGORY_ID)

        if category is None:
            await interaction.response.send_message(
                "Blad: kategoria ticketow nie istnieje.",
                ephemeral=True
            )
            return

        # ===== LIMIT 2 TICKETOW =====
        user_tickets = [
            ch for ch in category.channels
            if ch.name.startswith("ticket-") and interaction.user.name in ch.name
        ]

        if len(user_tickets) >= 2:
            await interaction.response.send_message(
                "Masz juz **2 aktywne tickety**. Zamknij jeden, aby stworzyc nowy.",
                ephemeral=True
            )
            return

        ticket_channel = await guild.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            category=category,
            overwrites={
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }
        )

        embed = discord.Embed(
            title="TICKET UTWORZONY",
            description=(
                f"{interaction.user.mention} ticket zostal utworzony.\n"
                f"Kategoria: **{self.values[0]}**\n"
                f"Napisz, w czym mozemy pomoc."
            ),
            color=discord.Color.green()
        )

        await ticket_channel.send(embed=embed, view=TicketPanel())

        await interaction.response.send_message(
            f"Twoj ticket zostal utworzony: {ticket_channel.mention}",
            ephemeral=True
        )


# ===== PRZYCISK ZAMKNIJ TICKET =====

class CloseTicketButton(Button):
    def __init__(self):
        super().__init__(
            label="Zamknij ticket",
            style=discord.ButtonStyle.danger,
            custom_id="close_ticket"  # <-- MUSI BYC
        )

    async def callback(self, interaction: discord.Interaction):
        channel = interaction.channel

        await interaction.response.send_message(
            "Ticket zostanie zamkniety za 3 sekundy...",
            ephemeral=True
        )

        await asyncio.sleep(3)
        await channel.delete()


class TicketPanel(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(CloseTicketButton())


# ===== WIDOK SELECTA =====

class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())


# ===== KOMENDA DO WYSYLANIA PANELU =====

@bot.command()
@commands.has_permissions(administrator=True)
async def setup_tickets(ctx):
    embed = discord.Embed(
        title="SYSTEM TICKETOW",
        description=(
            "1. Badz cierpliwy.\n"
            "2. Nie oznaczaj zarzadu.\n\n"
            "Wybierz odpowiednia kategorie swojej sprawy."
        ),
        color=discord.Color.green()
    )

    await ctx.send(embed=embed, view=TicketView())


# ===== REJESTRACJA WIDOKOW =====

@bot.event
async def on_ready():
    print(f"Zalogowano jako {bot.user}")
    bot.add_view(TicketView())     # select
    bot.add_view(TicketPanel())    # przycisk zamknij


# ===== POWITANIA =====
WELCOME_CHANNEL_ID = 1511836756570542262  # <-- tutaj wklej ID kanalu powitan

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel is None:
        return

    embed = discord.Embed(
        title="NOWY UZYTKOWNIK!",
        description=(
            f"{member.mention} dolaczyl na serwer!\n"
            f"Mamy teraz **{member.guild.member_count}** uzytkownikow.\n\n"
            "Udaj sie na kanal regulamin i zapoznaj sie z zasadami."
        ),
        color=0x2ecc71  # ladny zielony
    )

    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)

    await channel.send(embed=embed)


# ===== START =====
bot.run("MTUxNTA1MDYxNDc5MzY5OTQ0OA.GWLOkE.yMcdKBTI26N9ly428gA-nLPoQlFXKGQvTk2Hzs")

