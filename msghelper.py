class MessageHelper():
    def __init__(self, data):
        self.data = data

    async def build_reddit_title(self):
        """
        Build reddit title string
        [UN]LOADING | CARRIER NAME (123-ABC) | SYSTEM - STATION ([L|M|S] pads) | ##k profit | ##k Supply|Demand
        """
        quantity_type = 'Demand' if self.data['mission_type'] == 'loading' else 'Supply'
        reddit_title = (
            f"{self.data['mission_type'].upper()} | {self.data['carrier_name']}"
            f" | {self.data['system_name']} - {self.data['station_name']} ({self.data['pad_size']} pads)"
            f" | {self.data['commodity']} | {self.data['profit']}/t profit | {self.data['quantity']} {quantity_type}"
        )
        return reddit_title

    async def build_reddit_body(self):
        """
        Build reddit body string
            Carrier Name: carrier_name
            [Un]Loading: commodity 
            Station: station_name ([L|M|S] pads)
            System: system_name
            Profit: profit
            [Supply|Demand]: quantity
        """
        quantity_type = 'Demand' if self.data['mission_type'] == 'loading' else 'Supply'
        reddit_body = f"""
            Carrier Name: {self.data['carrier_name']}
            {self.data['mission_type'].title()}: {self.data['commodity']}
            Station: {self.data['station_name']} ({self.data['pad_size']} pads)
            System: {self.data['system_name']}
            Profit: {self.data['profit']}
            {quantity_type}: {self.data['quantity']}
        """
        return reddit_body

    async def build_discord_message(self):
        """
        Build Discord message to paste in channels
        ```
            **carrier_name** is [loading|unloading] **commodity** [to|from] **station_name** ([L|M|S] pads)
            in **system_name** profit/t profit, quanity [demand|supply]
        """
        if self.data['mission_type'] == 'loading':
            quantity_type = 'demand'
            verb = 'from'
        else:
            quantity_type = 'supply'
            verb = 'to'

        discord_paste = (
            f"```\n"
            f"**{self.data['carrier_name']}** is {self.data['mission_type']} **{self.data['commodity']}**"
            f" {verb} **{self.data['station_name']}** ({self.data['pad_size']} pads) in **{self.data['system_name']}**"
            f" {self.data['profit']}/t profit, {self.data['quantity']} {quantity_type}"
            f"\n```"
        )
        return discord_paste