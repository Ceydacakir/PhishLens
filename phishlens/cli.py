
import sys, json, csv, click
from .model import train, predict

@click.group()
def cli():
    pass

@cli.command("train")
@click.option("--data", "data_path", required=True, type=click.Path(exists=True))
@click.option("--model-out", required=True, type=click.Path())
def train_cmd(data_path, model_out):
    info = train(data_path, model_out)
    click.echo(json.dumps(info, ensure_ascii=False))

@cli.command("predict")
@click.option("--model", "model_path", required=True, type=click.Path(exists=True))
@click.option("--url", "single_url", type=str, default=None)
@click.option("--in", "in_path", type=click.Path(exists=True), default=None)
@click.option("--out", "out_path", type=click.Path(), default=None)
def predict_cmd(model_path, single_url, in_path, out_path):
    urls = []
    if single_url:
        urls = [single_url]
    elif in_path:
        urls = [l.strip() for l in open(in_path, encoding="utf-8") if l.strip()]
    else:
        urls = [l.strip() for l in sys.stdin if l.strip()]
    res = predict(model_path, urls)
    if out_path:
        with open(out_path, "w", encoding="utf-8", newline="") as f:
            wr = csv.writer(f); wr.writerow(["url","pred","prob"])
            for r in res: wr.writerow([r["url"], r["pred"], f"{r['prob']:.4f}"])
        click.echo(f"Wrote: {out_path}")
    else:
        click.echo(json.dumps(res, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    cli()
