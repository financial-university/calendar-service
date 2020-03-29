async def test_not_ok(api_client):
    async with api_client.get("calendar/group/rwersdf") as response:
        assert response.status == 404

    async with api_client.get("calendar/grop/9331") as response:
        assert response.status == 404


async def test_all_ok(api_client):
    async with api_client.get("calendar/group/9331") as response:
        assert response.status == 200
