
def check_budget(budget, cheap_hotel_available):
    """根据预算和便宜酒店的可用情况决定下一步。"""
    if budget >= 1000:
        return "book_hotel"
    elif cheap_hotel_available:
        return "find_cheaper_hotel"
    else:
        return "cancel_booking"


def book_hotel():
    print("[Book Hotel] 预订标准酒店")


def find_cheaper_hotel():
    print("[Find Cheaper Hotel] 预订前搜索更便宜的酒店")
    return False


def cancel_booking():
    print("[Cancel Booking] 没有合适的便宜酒店，取消预订")


def run_workflow(budget, cheap_hotel_available):
    print(f"当前预算：{budget} 元")
    print(f"是否有可用的便宜酒店：{cheap_hotel_available}")

    next_step = check_budget(budget, cheap_hotel_available)
    print(f"Workflow 选择下一步：{next_step}")

    if next_step == "book_hotel":
        book_hotel()
    elif next_step == "find_cheaper_hotel":
         available = find_cheaper_hotel()

         if available:
              print("[Workflow] 找到便宜酒店，继续预订")
         else:
                cancel_booking()	
    elif next_step == "cancel_booking":
        cancel_booking()

    print("Workflow 执行结束")


if __name__ == "__main__":
    print("========== 情况一 ==========")
    run_workflow(1500, True)

    print("\n========== 情况二 ==========")
    run_workflow(500, True)

    print("\n========== 情况三 ==========")
    run_workflow(500, False)

