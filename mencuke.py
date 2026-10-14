import fitz  # PyMuPDF
import os

def is_blank_page(page):
    """ページが実質的に白紙かどうかを判定する関数"""
    # テキストが含まれているか
    if page.get_text().strip():
        return False
    
    # 画像や描画要素（ベクターデータ）が含まれているか
    if page.get_images() or page.get_drawings():
        return False
    
    return True

def create_smart_mencuke():
    # --- 設定エリア ---
    input_folder = "./cards"
    input_base_pdf = "名刺10面フォーマット(両面).pdf"
    out_folder_single = "./output_single"  # 片面（裏面が白紙）用
    out_folder_double = "./output_double"  # 両面用

    MM_TO_PT = 72 / 25.4

    # 座標設定 (mm)
    start_x, start_y = 9.0, 7.0
    card_w, card_h = 91.0, 55.0
    v_gutter, h_gap = 2.0, 10.0

    # フォルダ作成
    for folder in [out_folder_single, out_folder_double]:
        if not os.path.exists(folder):
            os.makedirs(folder)

    # 1. フォルダ内のPDFファイル一覧を取得
    card_files = [f for f in os.listdir(input_folder) if f.lower().endswith(".pdf")]

    if not card_files:
        print("名刺データPDFが見つかりませんでした。")
        return

    # テンプレートを開く
    try:
        base_template = fitz.open(input_base_pdf)
    except Exception as e:
        print(f"台紙エラー: {e}")
        return

    for filename in card_files:
        card_path = os.path.join(input_folder, filename)
        
        with fitz.open(card_path) as card_doc:
            # 2ページ目が白紙かどうかをチェック
            # (全データ2ページある前提で、1インデックス=2ページ目を確認)
            if len(card_doc) >= 2:
                is_double = not is_blank_page(card_doc[1])
            else:
                is_double = False # そもそも1ページしかない場合
            
            # 出力用PDFの作成
            out_doc = fitz.open()
            
            # --- 表面の作成 ---
            out_doc.insert_pdf(base_template, from_page=0, to_page=0)
            page_front = out_doc[0]
            for idx in range(10):
                row, col = idx // 2, idx % 2
                x = start_x + (col * (card_w + h_gap))
                y = start_y + (row * (card_h + v_gutter))
                rect = fitz.Rect(x * MM_TO_PT, y * MM_TO_PT, (x + card_w) * MM_TO_PT, (y + card_h) * MM_TO_PT)
                page_front.show_pdf_page(rect, card_doc, 0, overlay=True)

            # --- 裏面の作成（2ページ目が白紙でない場合のみ） ---
            if is_double:
                out_doc.insert_pdf(base_template, from_page=1, to_page=1)
                page_back = out_doc[1]
                for idx in range(10):
                    row, col = idx // 2, idx % 2
                    back_col = 1 - col # 左右反転
                    x = start_x + (back_col * (card_w + h_gap))
                    y = start_y + (row * (card_h + v_gutter))
                    rect = fitz.Rect(x * MM_TO_PT, y * MM_TO_PT, (x + card_w) * MM_TO_PT, (y + card_h) * MM_TO_PT)
                    page_back.show_pdf_page(rect, card_doc, 1, overlay=True)

            # --- 保存先の振り分け ---
            if is_double:
                target_folder = out_folder_double
                suffix = "_両面"
            else:
                target_folder = out_folder_single
                suffix = "_片面"
            
            save_name = f"面付済み_{os.path.splitext(filename)[0]}{suffix}.pdf"
            out_doc.save(os.path.join(target_folder, save_name))
            out_doc.close()
            print(f"解析完了: {filename} -> {'両面' if is_double else '片面'}として出力しました")

    base_template.close()
    print("\nすべての仕分け・面付が完了しました。")

if __name__ == "__main__":
    create_smart_mencuke()