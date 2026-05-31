# Lightroom Classic HDR Merge Feasibility

Date: 2026-05-31

## Finding

`lr catalog find-brackets` should remain a bracket discovery and handoff command. Do not expose a Lightroom-native HDR merge command until a public Lightroom Classic Lua SDK API is verified live.

The current evidence supports:

- Bracket discovery can use Lightroom photo metadata. The SDK reference documents `photo:getRawMetadata("exposureBias")` as a numeric exposure compensation key, and `photo:getFormattedMetadata("exposureBias")` as the display form.
- Lightroom Classic HDR Photo Merge is documented as a UI workflow: select photos, choose **Photo > Photo Merge > HDR**, review the preview dialog, and click Merge.
- The installed Lightroom Classic 15.3 app bundle contains internal `PhotoMerge*.lua` resources, but those are not public SDK API and should not be called from this plugin.
- PhotomatixCL is a real external CLI HDR engine, but its vendor page lists Windows and Linux builds, not macOS. The separate Photomatix HDR Batch Plugin for Lightroom supports macOS and Lightroom Classic, but it is a Lightroom UI/plugin workflow, not a shell CLI available on this machine.

## Implemented Path

The CLI now reports bracket groups with per-result `groupId` values, warnings, and a `handoff` block. Agents can safely discover groups, compact the output with `--fields`, and hand the listed IDs/paths to Lightroom's manual HDR merge UI or to a separately verified external HDR engine.

Recommended command:

```bash
lr -o json --fields groups.groupId,groups.photos.id,groups.exposureBiases,count,warnings,handoff catalog find-brackets
```

For intentional catalog scans, add filters:

```bash
lr -o json catalog find-brackets --all --folder-path "/Shoot/Day1" --capture-date-from 2026-05-01 --file-format RAW
```

## Freshness Receipts

- Source: https://developer.adobe.com/lightroom-classic/  Version/date: current page fetched 2026-05-31  Notes: Adobe describes Lightroom Classic extensibility as Lua plugin SDK, metadata, export/publish, and UI extension surfaces.
- Source: https://archive.stecman.co.nz/files/docs/lightroom-sdk/API-Reference/modules/LrPhoto.html  Version/date: Lightroom SDK 5 archive, fetched 2026-05-31  Notes: `LrPhoto` documents `getRawMetadata("exposureBias")`, `getFormattedMetadata("exposureBias")`, and no Photo Merge/HDR merge API appears on `LrPhoto`.
- Source: https://helpx.adobe.com/lightroom-classic/help/hdr-photo-merge.html  Version/date: last updated Jul 29, 2024, fetched 2026-05-31  Notes: Adobe documents HDR merge as a Photo > Photo Merge > HDR UI workflow that creates a DNG.
- Source: https://fastmcp.wiki/en/servers/tools  Version/date: v3 docs, fetched 2026-05-31  Notes: FastMCP validates tools against explicit function signatures and does not support `*args`/`**kwargs`; this matches the schema-generated explicit signature approach.
- Source: https://www.hdrsoft.com/download/photomatixcl.html  Version/date: fetched 2026-05-31  Notes: PhotomatixCL can merge bracketed images via CLI, but vendor installation options are Windows and Linux.
- Source: https://www.hdrsoft.com/download/hdr-batch-lightroom-plugin.html  Version/date: fetched 2026-05-31  Notes: Photomatix HDR Batch Plugin supports Lightroom Classic on macOS, but is accessed through Lightroom UI/plugin menus.
