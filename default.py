import xbmc
import xbmcgui
import json
import xbmcvfs

LOG_FILE = xbmcvfs.translatePath('special://temp/reset_inprogress_episodes.log')

def log(msg):
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')

def get_inprogress_episodes():
    request = {
        "jsonrpc": "2.0",
        "method": "VideoLibrary.GetEpisodes",
        "params": {
            "properties": ["episode", "season", "showtitle", "resume"]
        },
        "id": 1
    }
    pDialog = xbmcgui.DialogProgress()
    pDialog.create('Reset In-Progress Episodes', 'Searching Episodes...')
    response = json.loads(xbmc.executeJSONRPC(json.dumps(request)))
    episodes = response.get("result", {}).get("episodes", [])
    if pDialog.iscanceled():
        return
    pDialog.update(80)
    inprogress = [ep for ep in episodes if ep.get("resume", {}).get("position", 0) > 0]
    log(f"Found {len(episodes)} total episodes, {len(inprogress)} in-progress")
    pDialog.close()
    return inprogress

def reset_episode_progress(episode):
    episode_id = episode["episodeid"]
    request = {
        "jsonrpc": "2.0",
        "method": "VideoLibrary.SetEpisodeDetails",
        "params": {
            "episodeid": episode_id,
            "resume": {"position": 0, "total": 0}
        },
        "id": 1
    }
    result = json.loads(xbmc.executeJSONRPC(json.dumps(request)))
    log(f"Reset '{episode['showtitle']}' (ID {episode_id}): {result}")

def main():
    episodes = get_inprogress_episodes()
    if not episodes:
        xbmcgui.Dialog().ok("Reset In-Progress Episodes", "No in-progress episodes found.")
        return

    num = len(episodes)
    confirm = xbmcgui.Dialog().yesno(
        "Reset In-Progress Episodes",
        f"Found {num} in-progress episodes. Reset their watch progress?",
        yeslabel="Reset",
        nolabel="Cancel"
    )
    if confirm:
        pDialog = xbmcgui.DialogProgress()
        pDialog.create('Reset In-Progress Episodes', 'Resetting episodes...')
        for index, ep in enumerate(episodes):
            pDialog.update((index * 100) // num, f"Resetting ({index + 1}/{num}): {ep['showtitle']} S{ep['season']:02d}E{ep['episode']:02d}")
            if pDialog.iscanceled():
                break
            reset_episode_progress(ep)
        pDialog.close()

        xbmcgui.Dialog().notification(
            "Kodi",
            f"Reset {len(episodes)} episodes",
            xbmcgui.NOTIFICATION_INFO,
            4000
        )
    else:
        xbmcgui.Dialog().notification(
            "Kodi",
            "No episodes were reset",
            xbmcgui.NOTIFICATION_INFO,
            3000
        )

if __name__ == "__main__":
    main()
