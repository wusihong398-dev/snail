"use client";

import {
  Card,
  Tabs,
  Table,
  Button,
  Space,
  Tag,
  Modal,
  Form,
  Input,
  InputNumber,
  Select,
  Switch,
  message,
  Statistic,
  Row,
  Col,
  Descriptions,
  DatePicker
} from "antd";

import {
  PlusOutlined,
  ReloadOutlined,
  EditOutlined,
  DeleteOutlined,
  ShoppingCartOutlined,
  CrownOutlined,
  FileTextOutlined,
  WalletOutlined,
  SearchOutlined,
  GiftOutlined,
  HeartOutlined
} from "@ant-design/icons";

import {
  useEffect,
  useMemo,
  useState
} from "react";

import api from "../../lib/api";


type ProductItem = {
  id: number;
  name: string;
  product_type: string;
  member_level: string | null;
  member_days: number | null;
  price_cents: number;
  coin_price: number;
  enabled: boolean;
  sort_order: number;
  description: string | null;
  created_at: string | null;
};


type OrderItem = {
  id: number;
  order_no: string;
  user_id: number;
  product_id: number;
  product_name: string;
  product_type: string;
  member_level: string | null;
  member_days: number | null;
  payment_method: string;
  amount_cents: number;
  coin_amount: number;
  status: string;
  created_at: string | null;
  paid_at: string | null;
};


type CoinTransactionItem = {
  id: number;
  user_id: number;
  transaction_type: string;
  amount: number;
  balance_before: number;
  balance_after: number;
  order_id: number | null;
  description: string | null;
  created_at: string | null;
};


type GiftConfigItem = {
  id: number;
  product_id: number;
  icon_url: string | null;
  rarity: string;
  exp_reward: number;
  intimacy_reward: number;
  created_at: string | null;
};


type GiftRecordItem = {
  id: number;
  order_id: number;
  sender_user_id: number;
  receiver_user_id: number;
  product_id: number;
  gift_name: string;
  quantity: number;
  coin_amount: number;
  exp_reward: number;
  intimacy_reward: number;
  created_at: string | null;
};


type EditableField =
  | "name"
  | "member_level"
  | "member_days"
  | "price_yuan"
  | "coin_price"
  | "sort_order"
  | "description";


type GiftEditableField =
  | "rarity"
  | "exp_reward"
  | "intimacy_reward"
  | "icon_url";


export default function ShopCenter() {

  const [products, setProducts] =
    useState<ProductItem[]>([]);

  const [orders, setOrders] =
    useState<OrderItem[]>([]);

  const [transactions, setTransactions] =
    useState<CoinTransactionItem[]>([]);

  const [giftConfigs, setGiftConfigs] =
    useState<GiftConfigItem[]>([]);

  const [giftRecords, setGiftRecords] =
    useState<GiftRecordItem[]>([]);


  const [loading, setLoading] =
    useState(false);


  const [createOpen, setCreateOpen] =
    useState(false);

  const [detailOpen, setDetailOpen] =
    useState(false);

  const [fieldOpen, setFieldOpen] =
    useState(false);

  const [orderDetailOpen, setOrderDetailOpen] =
    useState(false);

  const [giftDetailOpen, setGiftDetailOpen] =
    useState(false);

  const [giftFieldOpen, setGiftFieldOpen] =
    useState(false);

  const [giftConfigOpen, setGiftConfigOpen] =
    useState(false);


  const [currentProduct, setCurrentProduct] =
    useState<ProductItem | null>(null);

  const [currentOrder, setCurrentOrder] =
    useState<OrderItem | null>(null);

  const [currentGiftProduct, setCurrentGiftProduct] =
    useState<ProductItem | null>(null);

  const [currentGiftConfig, setCurrentGiftConfig] =
    useState<GiftConfigItem | null>(null);


  const [editingField, setEditingField] =
    useState<EditableField | null>(null);

  const [giftEditingField, setGiftEditingField] =
    useState<GiftEditableField | null>(null);


  const [orderKeyword, setOrderKeyword] =
    useState("");

  const [orderUserId, setOrderUserId] =
    useState("");

  const [orderStatus, setOrderStatus] =
    useState<string | undefined>();

  const [orderPayment, setOrderPayment] =
    useState<string | undefined>();

  const [orderDate, setOrderDate] =
    useState<string | null>(null);


  const [createForm] =
    Form.useForm();

  const [fieldForm] =
    Form.useForm();

  const [giftFieldForm] =
    Form.useForm();

  const [giftConfigForm] =
    Form.useForm();


  async function loadProducts() {

    try {

      const res =
        await api.get(
          "/shop/products"
        );

      setProducts(
        Array.isArray(res.data)
          ? res.data
          : []
      );

    } catch (error:any) {

      message.error(
        error?.response?.data?.detail
        || "读取商品失败"
      );

    }

  }


  async function loadOrders() {

    try {

      const res =
        await api.get(
          "/shop/orders"
        );

      setOrders(
        Array.isArray(res.data)
          ? res.data
          : []
      );

    } catch (error:any) {

      message.error(
        error?.response?.data?.detail
        || "读取订单失败"
      );

    }

  }


  async function loadTransactions() {

    try {

      const res =
        await api.get(
          "/shop/coin-transactions"
        );

      setTransactions(
        Array.isArray(res.data)
          ? res.data
          : []
      );

    } catch (error:any) {

      message.error(
        error?.response?.data?.detail
        || "读取蜗币流水失败"
      );

    }

  }


  async function loadGiftConfigs() {

    try {

      const res =
        await api.get(
          "/gifts/products"
        );

      setGiftConfigs(
        Array.isArray(res.data)
          ? res.data
          : []
      );

    } catch (error:any) {

      message.error(
        error?.response?.data?.detail
        || "读取礼物配置失败"
      );

    }

  }


  async function loadGiftRecords() {

    try {

      const res =
        await api.get(
          "/gifts/records"
        );

      setGiftRecords(
        Array.isArray(res.data)
          ? res.data
          : []
      );

    } catch (error:any) {

      message.error(
        error?.response?.data?.detail
        || "读取送礼记录失败"
      );

    }

  }


  async function loadAll() {

    setLoading(true);

    try {

      await Promise.all([
        loadProducts(),
        loadOrders(),
        loadTransactions(),
        loadGiftConfigs(),
        loadGiftRecords()
      ]);

    } finally {

      setLoading(false);

    }

  }


  useEffect(() => {

    loadAll();

  }, []);


  const statistics =
    useMemo(() => {

      const enabled =
        products.filter(
          item => item.enabled
        ).length;

      const member =
        products.filter(
          item =>
            item.product_type === "member"
        ).length;

      const vip =
        products.filter(
          item =>
            item.member_level === "vip"
        ).length;

      const svip =
        products.filter(
          item =>
            item.member_level === "svip"
        ).length;

      const paidOrders =
        orders.filter(
          item =>
            item.status === "paid"
        ).length;

      const coinSpent =
        transactions
          .filter(
            item =>
              item.amount < 0
          )
          .reduce(
            (
              total,
              item
            ) =>
              total
              + Math.abs(
                  item.amount
                ),
            0
          );

      const giftProducts =
        products.filter(
          item =>
            item.product_type === "gift"
        );

      const giftEnabled =
        giftProducts.filter(
          item => item.enabled
        ).length;

      const totalGiftQuantity =
        giftRecords.reduce(
          (
            total,
            item
          ) =>
            total
            + Number(
                item.quantity || 0
              ),
          0
        );

      const totalGiftCoins =
        giftRecords.reduce(
          (
            total,
            item
          ) =>
            total
            + Number(
                item.coin_amount || 0
              ),
          0
        );


      return {

        total:
          products.length,

        enabled,

        member,

        vip,

        svip,

        orderCount:
          orders.length,

        paidOrders,

        transactionCount:
          transactions.length,

        coinSpent,

        giftProductCount:
          giftProducts.length,

        giftEnabled,

        giftRecordCount:
          giftRecords.length,

        totalGiftQuantity,

        totalGiftCoins
      };

    }, [
      products,
      orders,
      transactions,
      giftRecords
    ]);


  const filteredOrders =
    useMemo(() => {

      return orders.filter(
        order => {

          if (
            orderKeyword
            && !order.order_no
              .toLowerCase()
              .includes(
                orderKeyword
                  .toLowerCase()
              )
          ) {
            return false;
          }


          if (
            orderUserId
            && String(order.user_id)
              !== orderUserId.trim()
          ) {
            return false;
          }


          if (
            orderStatus
            && order.status
              !== orderStatus
          ) {
            return false;
          }


          if (
            orderPayment
            && order.payment_method
              !== orderPayment
          ) {
            return false;
          }


          if (
            orderDate
            && order.created_at
          ) {

            const date =
              new Date(
                order.created_at
              );

            const yyyy =
              date.getFullYear();

            const mm =
              String(
                date.getMonth() + 1
              ).padStart(
                2,
                "0"
              );

            const dd =
              String(
                date.getDate()
              ).padStart(
                2,
                "0"
              );

            const localDate =
              `${yyyy}-${mm}-${dd}`;

            if (
              localDate
              !== orderDate
            ) {
              return false;
            }

          }


          return true;

        }
      );

    }, [
      orders,
      orderKeyword,
      orderUserId,
      orderStatus,
      orderPayment,
      orderDate
    ]);


  const memberProducts =
    products.filter(
      item =>
        item.product_type
        === "member"
    );


  const giftProducts =
    products.filter(
      item =>
        item.product_type
        === "gift"
    );


  function formatTime(
    value:string | null
  ) {

    if (!value) {
      return "-";
    }

    try {

      return new Date(
        value
      ).toLocaleString();

    } catch {

      return value;

    }

  }


  function productTypeName(
    value:string
  ) {

    switch (value) {

      case "member":
        return "会员";

      case "gift":
        return "礼物";

      case "pet":
        return "宠物";

      case "decoration":
        return "装扮";

      default:
        return value;

    }

  }


  function paymentName(
    value:string
  ) {

    switch (value) {

      case "coins":
        return "蜗币";

      case "wechat":
        return "微信支付";

      case "alipay":
        return "支付宝";

      case "apple":
        return "Apple";

      default:
        return value;

    }

  }


  function rarityName(
    value:string
  ) {

    switch (value) {

      case "normal":
        return "普通";

      case "rare":
        return "稀有";

      case "epic":
        return "史诗";

      case "legendary":
        return "传说";

      default:
        return value;

    }

  }


  function rarityColor(
    value:string
  ) {

    switch (value) {

      case "rare":
        return "blue";

      case "epic":
        return "purple";

      case "legendary":
        return "gold";

      default:
        return "default";

    }

  }


  function renderMemberLevel(
    value:string | null
  ) {

    if (value === "svip") {

      return (
        <Tag color="gold">
          SVIP
        </Tag>
      );

    }

    if (value === "vip") {

      return (
        <Tag color="purple">
          VIP
        </Tag>
      );

    }

    return "-";

  }


  function getGiftConfig(
    productId:number
  ) {

    return giftConfigs.find(
      item =>
        item.product_id
        === productId
    ) || null;

  }


  function openCreate(
    productType = "member"
  ) {

    createForm.resetFields();

    createForm.setFieldsValue({

      product_type:
        productType,

      member_level:
        "vip",

      member_days:
        30,

      price_yuan:
        productType === "gift"
          ? 0
          : 19.9,

      coin_price:
        productType === "gift"
          ? 50
          : 1990,

      enabled:
        true,

      sort_order:
        10,

      description:
        ""

    });

    setCreateOpen(true);

  }


  async function saveCreate() {

    try {

      const values =
        await createForm
          .validateFields();


      const payload = {

        name:
          values.name,

        product_type:
          values.product_type,

        member_level:
          values.product_type
          === "member"
            ? values.member_level
            : null,

        member_days:
          values.product_type
          === "member"
            ? Number(
                values.member_days
              )
            : null,

        price_cents:
          Math.round(
            Number(
              values.price_yuan
              || 0
            ) * 100
          ),

        coin_price:
          Number(
            values.coin_price
            || 0
          ),

        enabled:
          Boolean(
            values.enabled
          ),

        sort_order:
          Number(
            values.sort_order
            || 0
          ),

        description:
          values.description
          || null
      };


      await api.post(
        "/shop/products",
        payload
      );


      message.success(
        "商品添加成功"
      );


      setCreateOpen(false);

      createForm.resetFields();

      await loadProducts();


    } catch (error:any) {

      if (
        error?.errorFields
      ) {
        return;
      }

      message.error(
        error?.response?.data?.detail
        || "新增商品失败"
      );

    }

  }


  function openDetail(
    product:ProductItem
  ) {

    setCurrentProduct(
      product
    );

    setDetailOpen(true);

  }


  function openOrderDetail(
    order:OrderItem
  ) {

    setCurrentOrder(
      order
    );

    setOrderDetailOpen(
      true
    );

  }


  function openFieldEditor(
    field:EditableField
  ) {

    if (!currentProduct) {
      return;
    }

    setEditingField(field);

    fieldForm.resetFields();


    switch (field) {

      case "name":

        fieldForm.setFieldsValue({
          value:
            currentProduct.name
        });

        break;


      case "member_level":

        fieldForm.setFieldsValue({
          value:
            currentProduct.member_level
            || "vip"
        });

        break;


      case "member_days":

        fieldForm.setFieldsValue({
          value:
            currentProduct.member_days
            || 30
        });

        break;


      case "price_yuan":

        fieldForm.setFieldsValue({
          value:
            Number(
              currentProduct.price_cents
              || 0
            ) / 100
        });

        break;


      case "coin_price":

        fieldForm.setFieldsValue({
          value:
            currentProduct.coin_price
            || 0
        });

        break;


      case "sort_order":

        fieldForm.setFieldsValue({
          value:
            currentProduct.sort_order
            || 0
        });

        break;


      case "description":

        fieldForm.setFieldsValue({
          value:
            currentProduct.description
            || ""
        });

        break;

    }


    setFieldOpen(true);

  }


  async function saveField() {

    if (
      !currentProduct
      || !editingField
    ) {
      return;
    }

    try {

      const values =
        await fieldForm
          .validateFields();

      let payload:Record<
        string,
        unknown
      > = {};


      switch (
        editingField
      ) {

        case "name":

          payload = {
            name:
              values.value
          };

          break;


        case "member_level":

          payload = {
            member_level:
              values.value
          };

          break;


        case "member_days":

          payload = {
            member_days:
              Number(
                values.value
              )
          };

          break;


        case "price_yuan":

          payload = {
            price_cents:
              Math.round(
                Number(
                  values.value
                  || 0
                ) * 100
              )
          };

          break;


        case "coin_price":

          payload = {
            coin_price:
              Number(
                values.value
                || 0
              )
          };

          break;


        case "sort_order":

          payload = {
            sort_order:
              Number(
                values.value
                || 0
              )
          };

          break;


        case "description":

          payload = {
            description:
              values.value
              || null
          };

          break;

      }


      const res =
        await api.put(
          `/shop/products/${currentProduct.id}`,
          payload
        );


      setCurrentProduct(
        res.data
      );


      message.success(
        "保存成功"
      );


      setFieldOpen(false);

      setEditingField(null);

      await loadProducts();


    } catch (error:any) {

      if (
        error?.errorFields
      ) {
        return;
      }

      message.error(
        error?.response?.data?.detail
        || "保存失败"
      );

    }

  }


  async function toggleEnabled(
    product:ProductItem
  ) {

    try {

      const res =
        await api.patch(
          `/shop/products/${product.id}/enabled`
        );


      const updated =
        res.data;


      message.success(
        updated.enabled
          ? "商品已上架"
          : "商品已下架"
      );


      if (
        currentProduct
        && currentProduct.id
        === updated.id
      ) {

        setCurrentProduct(
          updated
        );

      }


      if (
        currentGiftProduct
        && currentGiftProduct.id
        === updated.id
      ) {

        setCurrentGiftProduct(
          updated
        );

      }


      await loadProducts();


    } catch (error:any) {

      message.error(
        error?.response?.data?.detail
        || "状态修改失败"
      );

    }

  }


  function remove(
    product:ProductItem
  ) {

    Modal.confirm({

      title:
        "删除商品",

      content:
        `确定删除“${product.name}”吗？`,

      okText:
        "删除",

      cancelText:
        "取消",

      okButtonProps: {
        danger:true
      },


      async onOk() {

        try {

          await api.delete(
            `/shop/products/${product.id}`
          );


          message.success(
            "商品已删除"
          );


          setDetailOpen(
            false
          );

          setCurrentProduct(
            null
          );


          await loadProducts();


        } catch (error:any) {

          message.error(
            error?.response?.data?.detail
            || "删除失败"
          );

        }

      }

    });

  }


  function openGiftDetail(
    product:ProductItem
  ) {

    const config =
      getGiftConfig(
        product.id
      );

    setCurrentGiftProduct(
      product
    );

    setCurrentGiftConfig(
      config
    );

    setGiftDetailOpen(
      true
    );

  }


  function openGiftConfigCreate(
    product:ProductItem
  ) {

    setCurrentGiftProduct(
      product
    );

    giftConfigForm.resetFields();

    giftConfigForm.setFieldsValue({

      icon_url:
        "",

      rarity:
        "normal",

      exp_reward:
        10,

      intimacy_reward:
        5

    });

    setGiftConfigOpen(
      true
    );

  }


  async function saveGiftConfigCreate() {

    if (
      !currentGiftProduct
    ) {
      return;
    }

    try {

      const values =
        await giftConfigForm
          .validateFields();


      await api.post(
        "/gifts/products",
        {

          product_id:
            currentGiftProduct.id,

          icon_url:
            values.icon_url
            || "",

          rarity:
            values.rarity,

          exp_reward:
            Number(
              values.exp_reward
              || 0
            ),

          intimacy_reward:
            Number(
              values.intimacy_reward
              || 0
            )

        }
      );


      message.success(
        "礼物配置创建成功"
      );


      setGiftConfigOpen(
        false
      );

      await loadGiftConfigs();


    } catch (error:any) {

      if (
        error?.errorFields
      ) {
        return;
      }

      message.error(
        error?.response?.data?.detail
        || "礼物配置保存失败"
      );

    }

  }


  function openGiftFieldEditor(
    field:GiftEditableField
  ) {

    if (
      !currentGiftConfig
    ) {
      return;
    }

    setGiftEditingField(
      field
    );

    giftFieldForm.resetFields();


    switch (field) {

      case "rarity":

        giftFieldForm.setFieldsValue({
          value:
            currentGiftConfig.rarity
        });

        break;


      case "exp_reward":

        giftFieldForm.setFieldsValue({
          value:
            currentGiftConfig.exp_reward
        });

        break;


      case "intimacy_reward":

        giftFieldForm.setFieldsValue({
          value:
            currentGiftConfig.intimacy_reward
        });

        break;


      case "icon_url":

        giftFieldForm.setFieldsValue({
          value:
            currentGiftConfig.icon_url
            || ""
        });

        break;

    }


    setGiftFieldOpen(
      true
    );

  }


  async function saveGiftField() {

    if (
      !currentGiftConfig
      || !giftEditingField
    ) {
      return;
    }

    try {

      const values =
        await giftFieldForm
          .validateFields();


      let payload:Record<
        string,
        unknown
      > = {};


      if (
        giftEditingField
        === "rarity"
      ) {

        payload = {
          rarity:
            values.value
        };

      }


      if (
        giftEditingField
        === "exp_reward"
      ) {

        payload = {
          exp_reward:
            Number(
              values.value
              || 0
            )
        };

      }


      if (
        giftEditingField
        === "intimacy_reward"
      ) {

        payload = {
          intimacy_reward:
            Number(
              values.value
              || 0
            )
        };

      }


      if (
        giftEditingField
        === "icon_url"
      ) {

        payload = {
          icon_url:
            values.value
            || ""
        };

      }


      const res =
        await api.put(
          `/gifts/products/${currentGiftConfig.id}`,
          payload
        );


      setCurrentGiftConfig(
        res.data
      );


      message.success(
        "礼物配置保存成功"
      );


      setGiftFieldOpen(
        false
      );

      setGiftEditingField(
        null
      );


      await loadGiftConfigs();


    } catch (error:any) {

      if (
        error?.errorFields
      ) {
        return;
      }

      message.error(
        error?.response?.data?.detail
        || "礼物配置保存失败"
      );

    }

  }


  function editButton(
    field:EditableField
  ) {

    return (

      <Button
        size="small"
        icon={
          <EditOutlined />
        }
        onClick={() =>
          openFieldEditor(
            field
          )
        }
      >
        编辑
      </Button>

    );

  }


  function giftEditButton(
    field:GiftEditableField
  ) {

    return (

      <Button
        size="small"
        icon={
          <EditOutlined />
        }
        onClick={() =>
          openGiftFieldEditor(
            field
          )
        }
      >
        编辑
      </Button>

    );

  }


  const productColumns = [

    {
      title:"商品名称",
      dataIndex:"name"
    },

    {
      title:"类型",
      dataIndex:"product_type",
      render:(
        value:string
      ) => (
        <Tag>
          {
            productTypeName(
              value
            )
          }
        </Tag>
      )
    },

    {
      title:"会员等级",
      dataIndex:"member_level",
      render:(
        value:string | null
      ) => (
        renderMemberLevel(
          value
        )
      )
    },

    {
      title:"有效期",
      dataIndex:"member_days",
      render:(
        value:number | null
      ) => (
        value
          ? `${value}天`
          : "-"
      )
    },

    {
      title:"人民币价格",
      dataIndex:"price_cents",
      render:(
        value:number
      ) => (
        `¥${(
          Number(
            value || 0
          ) / 100
        ).toFixed(2)}`
      )
    },

    {
      title:"蜗币价格",
      dataIndex:"coin_price"
    },

    {
      title:"状态",
      dataIndex:"enabled",
      render:(
        value:boolean
      ) => (
        <Tag
          color={
            value
              ? "green"
              : "default"
          }
        >
          {
            value
              ? "已上架"
              : "已下架"
          }
        </Tag>
      )
    },

    {
      title:"操作",
      render:(
        _:unknown,
        product:ProductItem
      ) => (
        <Space wrap>

          <Button
            type="primary"
            onClick={() =>
              openDetail(
                product
              )
            }
          >
            查看 / 编辑
          </Button>

          <Button
            onClick={() =>
              toggleEnabled(
                product
              )
            }
          >
            {
              product.enabled
                ? "下架"
                : "上架"
            }
          </Button>

          <Button
            danger
            icon={
              <DeleteOutlined />
            }
            onClick={() =>
              remove(
                product
              )
            }
          >
            删除
          </Button>

        </Space>
      )
    }

  ];


  const orderColumns = [

    {
      title:"订单号",
      dataIndex:"order_no",
      width:240
    },

    {
      title:"用户ID",
      dataIndex:"user_id"
    },

    {
      title:"商品",
      dataIndex:"product_name"
    },

    {
      title:"支付方式",
      dataIndex:"payment_method",
      render:(
        value:string
      ) => (
        paymentName(
          value
        )
      )
    },

    {
      title:"蜗币金额",
      dataIndex:"coin_amount"
    },

    {
      title:"状态",
      dataIndex:"status",
      render:(
        value:string
      ) => (
        <Tag
          color={
            value === "paid"
              ? "green"
              : value === "pending"
                ? "orange"
                : "red"
          }
        >
          {
            value === "paid"
              ? "已支付"
              : value === "pending"
                ? "待支付"
                : value
          }
        </Tag>
      )
    },

    {
      title:"创建时间",
      dataIndex:"created_at",
      render:(
        value:string | null
      ) => (
        formatTime(
          value
        )
      )
    },

    {
      title:"操作",
      render:(
        _:unknown,
        order:OrderItem
      ) => (
        <Button
          type="primary"
          onClick={() =>
            openOrderDetail(
              order
            )
          }
        >
          查看详情
        </Button>
      )
    }

  ];


  const transactionColumns = [

    {
      title:"用户ID",
      dataIndex:"user_id"
    },

    {
      title:"类型",
      dataIndex:"transaction_type",
      render:(
        value:string
      ) => (
        <Tag color="blue">
          {
            value === "purchase"
              ? "商品消费"
              : value === "gift"
                ? "送礼消费"
                : value
          }
        </Tag>
      )
    },

    {
      title:"变动数量",
      dataIndex:"amount",
      render:(
        value:number
      ) => (
        <Tag
          color={
            value < 0
              ? "red"
              : "green"
          }
        >
          {
            value > 0
              ? `+${value}`
              : value
          }
        </Tag>
      )
    },

    {
      title:"变动前",
      dataIndex:"balance_before"
    },

    {
      title:"变动后",
      dataIndex:"balance_after"
    },

    {
      title:"关联订单",
      dataIndex:"order_id",
      render:(
        value:number | null
      ) => (
        value
          ? `#${value}`
          : "-"
      )
    },

    {
      title:"说明",
      dataIndex:"description"
    },

    {
      title:"时间",
      dataIndex:"created_at",
      render:(
        value:string | null
      ) => (
        formatTime(
          value
        )
      )
    }

  ];


  const giftColumns = [

    {
      title:"礼物名称",

      render:(
        _:unknown,
        product:ProductItem
      ) => (
        product.name
      )
    },

    {
      title:"蜗币价格",

      render:(
        _:unknown,
        product:ProductItem
      ) => (
        product.coin_price
      )
    },

    {
      title:"稀有度",

      render:(
        _:unknown,
        product:ProductItem
      ) => {

        const config =
          getGiftConfig(
            product.id
          );

        if (!config) {

          return (
            <Tag color="red">
              未配置
            </Tag>
          );

        }

        return (
          <Tag
            color={
              rarityColor(
                config.rarity
              )
            }
          >
            {
              rarityName(
                config.rarity
              )
            }
          </Tag>
        );

      }
    },

    {
      title:"经验奖励",

      render:(
        _:unknown,
        product:ProductItem
      ) => {

        const config =
          getGiftConfig(
            product.id
          );

        return (
          config
            ? config.exp_reward
            : "-"
        );

      }
    },

    {
      title:"亲密度",

      render:(
        _:unknown,
        product:ProductItem
      ) => {

        const config =
          getGiftConfig(
            product.id
          );

        return (
          config
            ? config.intimacy_reward
            : "-"
        );

      }
    },

    {
      title:"状态",
      dataIndex:"enabled",

      render:(
        value:boolean
      ) => (
        <Tag
          color={
            value
              ? "green"
              : "default"
          }
        >
          {
            value
              ? "已上架"
              : "已下架"
          }
        </Tag>
      )
    },

    {
      title:"操作",

      render:(
        _:unknown,
        product:ProductItem
      ) => {

        const config =
          getGiftConfig(
            product.id
          );

        return (

          <Space wrap>

            {
              config
                ? (

                  <Button
                    type="primary"
                    onClick={() =>
                      openGiftDetail(
                        product
                      )
                    }
                  >
                    查看 / 编辑
                  </Button>

                )
                : (

                  <Button
                    type="primary"
                    onClick={() =>
                      openGiftConfigCreate(
                        product
                      )
                    }
                  >
                    完成礼物配置
                  </Button>

                )
            }


            <Button
              onClick={() =>
                toggleEnabled(
                  product
                )
              }
            >
              {
                product.enabled
                  ? "下架"
                  : "上架"
              }
            </Button>

          </Space>

        );

      }
    }

  ];


  const giftRecordColumns = [

    {
      title:"发送用户",
      dataIndex:"sender_user_id",
      render:(
        value:number
      ) => (
        `#${value}`
      )
    },

    {
      title:"接收用户",
      dataIndex:"receiver_user_id",
      render:(
        value:number
      ) => (
        `#${value}`
      )
    },

    {
      title:"礼物",
      dataIndex:"gift_name"
    },

    {
      title:"数量",
      dataIndex:"quantity"
    },

    {
      title:"消费蜗币",
      dataIndex:"coin_amount"
    },

    {
      title:"经验奖励",
      dataIndex:"exp_reward"
    },

    {
      title:"亲密度奖励",
      dataIndex:"intimacy_reward"
    },

    {
      title:"关联订单",
      dataIndex:"order_id",
      render:(
        value:number
      ) => (
        `#${value}`
      )
    },

    {
      title:"时间",
      dataIndex:"created_at",
      render:(
        value:string | null
      ) => (
        formatTime(
          value
        )
      )
    }

  ];


  const productContent = (

    <>

      <Row
        gutter={[16,16]}
        style={{
          marginBottom:20
        }}
      >

        <Col
          xs={24}
          md={8}
        >
          <Card>
            <Statistic
              title="商品总数"
              value={
                statistics.total
              }
              prefix={
                <ShoppingCartOutlined />
              }
            />
          </Card>
        </Col>

        <Col
          xs={24}
          md={8}
        >
          <Card>
            <Statistic
              title="已上架"
              value={
                statistics.enabled
              }
            />
          </Card>
        </Col>

        <Col
          xs={24}
          md={8}
        >
          <Card>
            <Statistic
              title="会员商品"
              value={
                statistics.member
              }
              prefix={
                <CrownOutlined />
              }
            />
          </Card>
        </Col>

      </Row>


      <Table
        rowKey="id"
        loading={loading}
        columns={productColumns}
        dataSource={products}
        scroll={{
          x:1100
        }}
      />

    </>

  );


  const memberContent = (

    <Table
      rowKey="id"
      loading={loading}
      columns={productColumns}
      dataSource={
        memberProducts
      }
      scroll={{
        x:1100
      }}
    />

  );


  const orderContent = (

    <>

      <Card
        size="small"
        style={{
          marginBottom:16
        }}
      >

        <Space wrap>

          <Input
            allowClear
            prefix={
              <SearchOutlined />
            }
            placeholder="搜索订单号"
            value={
              orderKeyword
            }
            onChange={
              e =>
                setOrderKeyword(
                  e.target.value
                )
            }
            style={{
              width:240
            }}
          />

          <Input
            allowClear
            placeholder="用户ID"
            value={
              orderUserId
            }
            onChange={
              e =>
                setOrderUserId(
                  e.target.value
                )
            }
            style={{
              width:130
            }}
          />

          <Select
            allowClear
            placeholder="订单状态"
            value={
              orderStatus
            }
            onChange={
              value =>
                setOrderStatus(
                  value
                )
            }
            style={{
              width:140
            }}
            options={[
              {
                label:"已支付",
                value:"paid"
              },
              {
                label:"待支付",
                value:"pending"
              }
            ]}
          />

          <Select
            allowClear
            placeholder="支付方式"
            value={
              orderPayment
            }
            onChange={
              value =>
                setOrderPayment(
                  value
                )
            }
            style={{
              width:140
            }}
            options={[
              {
                label:"蜗币",
                value:"coins"
              }
            ]}
          />

          <DatePicker
            placeholder="订单日期"
            onChange={(
              value,
              dateString
            ) => {

              setOrderDate(
                value
                  ? String(
                      dateString
                    )
                  : null
              );

            }}
          />

          <Button
            onClick={() => {

              setOrderKeyword("");
              setOrderUserId("");
              setOrderStatus(undefined);
              setOrderPayment(undefined);
              setOrderDate(null);

            }}
          >
            清空筛选
          </Button>

        </Space>

      </Card>


      <Table
        rowKey="id"
        loading={loading}
        columns={orderColumns}
        dataSource={
          filteredOrders
        }
        scroll={{
          x:1200
        }}
      />

    </>

  );


  const transactionContent = (

    <Table
      rowKey="id"
      loading={loading}
      columns={transactionColumns}
      dataSource={
        transactions
      }
      scroll={{
        x:1100
      }}
    />

  );


  const giftContent = (

    <>

      <Row
        gutter={[16,16]}
        style={{
          marginBottom:20
        }}
      >

        <Col
          xs={24}
          md={8}
        >
          <Card>
            <Statistic
              title="礼物商品"
              value={
                statistics.giftProductCount
              }
              prefix={
                <GiftOutlined />
              }
            />
          </Card>
        </Col>

        <Col
          xs={24}
          md={8}
        >
          <Card>
            <Statistic
              title="已上架礼物"
              value={
                statistics.giftEnabled
              }
            />
          </Card>
        </Col>

        <Col
          xs={24}
          md={8}
        >
          <Card>
            <Statistic
              title="累计送出"
              value={
                statistics.totalGiftQuantity
              }
            />
          </Card>
        </Col>

      </Row>


      <div
        style={{
          display:"flex",
          justifyContent:"flex-end",
          marginBottom:16
        }}
      >

        <Button
          type="primary"
          icon={
            <PlusOutlined />
          }
          onClick={() =>
            openCreate(
              "gift"
            )
          }
        >
          新增礼物商品
        </Button>

      </div>


      <Table
        rowKey="id"
        loading={loading}
        columns={giftColumns}
        dataSource={
          giftProducts
        }
        scroll={{
          x:950
        }}
      />


      <Card
        title="🎁 送礼记录"
        style={{
          marginTop:24
        }}
      >

        <Table
          rowKey="id"
          loading={loading}
          columns={
            giftRecordColumns
          }
          dataSource={
            giftRecords
          }
          scroll={{
            x:1100
          }}
        />

      </Card>

    </>

  );


  function placeholder(
    title:string,
    description:string
  ) {

    return (

      <Card>

        <h2>
          {title}
        </h2>

        <p
          style={{
            color:"#888"
          }}
        >
          {description}
        </p>

      </Card>

    );

  }


  function fieldTitle() {

    switch (
      editingField
    ) {

      case "name":
        return "编辑商品名称";

      case "member_level":
        return "编辑会员等级";

      case "member_days":
        return "编辑会员有效天数";

      case "price_yuan":
        return "编辑人民币价格";

      case "coin_price":
        return "编辑蜗币价格";

      case "sort_order":
        return "编辑排序";

      case "description":
        return "编辑商品说明";

      default:
        return "编辑商品";

    }

  }


  function fieldEditor() {

    switch (
      editingField
    ) {

      case "name":

        return (
          <Form.Item
            label="商品名称"
            name="value"
          >
            <Input />
          </Form.Item>
        );


      case "member_level":

        return (
          <Form.Item
            label="会员等级"
            name="value"
          >
            <Select
              options={[
                {
                  label:"VIP",
                  value:"vip"
                },
                {
                  label:"SVIP",
                  value:"svip"
                }
              ]}
            />
          </Form.Item>
        );


      case "member_days":

        return (
          <Form.Item
            label="有效天数"
            name="value"
          >
            <InputNumber
              min={1}
              style={{
                width:"100%"
              }}
            />
          </Form.Item>
        );


      case "price_yuan":

        return (
          <Form.Item
            label="人民币价格"
            name="value"
          >
            <InputNumber
              min={0}
              precision={2}
              style={{
                width:"100%"
              }}
            />
          </Form.Item>
        );


      case "coin_price":

        return (
          <Form.Item
            label="蜗币价格"
            name="value"
          >
            <InputNumber
              min={0}
              style={{
                width:"100%"
              }}
            />
          </Form.Item>
        );


      case "sort_order":

        return (
          <Form.Item
            label="排序"
            name="value"
          >
            <InputNumber
              style={{
                width:"100%"
              }}
            />
          </Form.Item>
        );


      case "description":

        return (
          <Form.Item
            label="商品说明"
            name="value"
          >
            <Input.TextArea
              rows={5}
            />
          </Form.Item>
        );


      default:

        return null;

    }

  }


  function giftFieldTitle() {

    switch (
      giftEditingField
    ) {

      case "rarity":
        return "编辑礼物稀有度";

      case "exp_reward":
        return "编辑经验奖励";

      case "intimacy_reward":
        return "编辑亲密度奖励";

      case "icon_url":
        return "编辑礼物图标";

      default:
        return "编辑礼物";
    }

  }


  function giftFieldEditor() {

    switch (
      giftEditingField
    ) {

      case "rarity":

        return (
          <Form.Item
            label="稀有度"
            name="value"
          >
            <Select
              options={[
                {
                  label:"普通",
                  value:"normal"
                },
                {
                  label:"稀有",
                  value:"rare"
                },
                {
                  label:"史诗",
                  value:"epic"
                },
                {
                  label:"传说",
                  value:"legendary"
                }
              ]}
            />
          </Form.Item>
        );


      case "exp_reward":

        return (
          <Form.Item
            label="经验奖励"
            name="value"
          >
            <InputNumber
              min={0}
              style={{
                width:"100%"
              }}
            />
          </Form.Item>
        );


      case "intimacy_reward":

        return (
          <Form.Item
            label="亲密度奖励"
            name="value"
          >
            <InputNumber
              min={0}
              style={{
                width:"100%"
              }}
            />
          </Form.Item>
        );


      case "icon_url":

        return (
          <Form.Item
            label="礼物图标地址"
            name="value"
          >
            <Input />
          </Form.Item>
        );


      default:

        return null;
    }

  }


  return (

    <Card>

      <div
        style={{
          display:"flex",
          alignItems:"center",
          justifyContent:"space-between",
          marginBottom:16
        }}
      >

        <div>

          <h1
            style={{
              margin:0
            }}
          >
            🛒 商业中心
          </h1>

          <div
            style={{
              color:"#888",
              marginTop:6
            }}
          >
            管理商品、会员、订单、蜗币和互动礼物
          </div>

        </div>


        <Space>

          <Button
            icon={
              <ReloadOutlined />
            }
            onClick={
              loadAll
            }
          >
            全部刷新
          </Button>

          <Button
            type="primary"
            icon={
              <PlusOutlined />
            }
            onClick={() =>
              openCreate()
            }
          >
            新增商品
          </Button>

        </Space>

      </div>


      <Tabs
        items={[
          {
            key:"products",
            label:"商品管理",
            children:
              productContent
          },

          {
            key:"members",
            label:"会员商品",
            children:
              memberContent
          },

          {
            key:"orders",
            label:"订单管理",
            children:
              orderContent
          },

          {
            key:"transactions",
            label:"蜗币流水",
            children:
              transactionContent
          },

          {
            key:"gifts",
            label:"礼物管理",
            children:
              giftContent
          },

          {
            key:"pets",
            label:"宠物管理",
            children:
              placeholder(
                "🐾 宠物管理",
                "下一阶段接入宠物商品、拥有关系和成长系统。"
              )
          },

          {
            key:"decorations",
            label:"装扮管理",
            children:
              placeholder(
                "🎨 装扮管理",
                "下一阶段接入头像框、昵称颜色和群身份装扮。"
              )
          }
        ]}
      />


      <Modal
        title="新增商品"
        open={
          createOpen
        }
        onOk={
          saveCreate
        }
        onCancel={() => {

          setCreateOpen(
            false
          );

          createForm.resetFields();

        }}
        okText="保存"
        cancelText="取消"
        width={650}
      >

        <Form
          form={
            createForm
          }
          layout="vertical"
        >

          <Form.Item
            label="商品名称"
            name="name"
            rules={[
              {
                required:true
              }
            ]}
          >
            <Input />
          </Form.Item>


          <Form.Item
            label="商品类型"
            name="product_type"
          >
            <Select
              options={[
                {
                  label:"会员",
                  value:"member"
                },
                {
                  label:"礼物",
                  value:"gift"
                },
                {
                  label:"宠物",
                  value:"pet"
                },
                {
                  label:"装扮",
                  value:"decoration"
                }
              ]}
            />
          </Form.Item>


          <Form.Item
            noStyle
            shouldUpdate
          >

            {({
              getFieldValue
            }) => {

              const type =
                getFieldValue(
                  "product_type"
                );

              if (
                type !== "member"
              ) {

                return null;

              }

              return (

                <>

                  <Form.Item
                    label="会员等级"
                    name="member_level"
                  >
                    <Select
                      options={[
                        {
                          label:"VIP",
                          value:"vip"
                        },
                        {
                          label:"SVIP",
                          value:"svip"
                        }
                      ]}
                    />
                  </Form.Item>


                  <Form.Item
                    label="会员有效天数"
                    name="member_days"
                  >
                    <InputNumber
                      min={1}
                      style={{
                        width:"100%"
                      }}
                    />
                  </Form.Item>

                </>

              );

            }}

          </Form.Item>


          <Form.Item
            label="人民币价格"
            name="price_yuan"
          >
            <InputNumber
              min={0}
              precision={2}
              style={{
                width:"100%"
              }}
            />
          </Form.Item>


          <Form.Item
            label="蜗币价格"
            name="coin_price"
          >
            <InputNumber
              min={0}
              style={{
                width:"100%"
              }}
            />
          </Form.Item>


          <Form.Item
            label="排序"
            name="sort_order"
          >
            <InputNumber
              style={{
                width:"100%"
              }}
            />
          </Form.Item>


          <Form.Item
            label="商品说明"
            name="description"
          >
            <Input.TextArea
              rows={4}
            />
          </Form.Item>


          <Form.Item
            label="立即上架"
            name="enabled"
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>

        </Form>

      </Modal>


      <Modal
        title={
          currentProduct
            ? `商品详情 - ${currentProduct.name}`
            : "商品详情"
        }
        open={
          detailOpen
        }
        footer={null}
        onCancel={() => {

          setDetailOpen(
            false
          );

          setCurrentProduct(
            null
          );

        }}
        width={720}
      >

        {
          currentProduct
          && (

            <Descriptions
              bordered
              column={1}
            >

              <Descriptions.Item
                label="商品名称"
              >
                <Space>
                  {
                    currentProduct.name
                  }
                  {
                    editButton(
                      "name"
                    )
                  }
                </Space>
              </Descriptions.Item>


              <Descriptions.Item
                label="商品类型"
              >
                {
                  productTypeName(
                    currentProduct.product_type
                  )
                }
              </Descriptions.Item>


              {
                currentProduct.product_type
                === "member"
                && (

                  <>

                    <Descriptions.Item
                      label="会员等级"
                    >
                      <Space>
                        {
                          renderMemberLevel(
                            currentProduct.member_level
                          )
                        }
                        {
                          editButton(
                            "member_level"
                          )
                        }
                      </Space>
                    </Descriptions.Item>


                    <Descriptions.Item
                      label="有效天数"
                    >
                      <Space>
                        {
                          currentProduct.member_days
                          || 0
                        }天
                        {
                          editButton(
                            "member_days"
                          )
                        }
                      </Space>
                    </Descriptions.Item>

                  </>

                )
              }


              <Descriptions.Item
                label="人民币价格"
              >
                <Space>
                  ¥{
                    (
                      Number(
                        currentProduct.price_cents
                        || 0
                      ) / 100
                    ).toFixed(2)
                  }
                  {
                    editButton(
                      "price_yuan"
                    )
                  }
                </Space>
              </Descriptions.Item>


              <Descriptions.Item
                label="蜗币价格"
              >
                <Space>
                  {
                    currentProduct.coin_price
                  }
                  {
                    editButton(
                      "coin_price"
                    )
                  }
                </Space>
              </Descriptions.Item>


              <Descriptions.Item
                label="排序"
              >
                <Space>
                  {
                    currentProduct.sort_order
                  }
                  {
                    editButton(
                      "sort_order"
                    )
                  }
                </Space>
              </Descriptions.Item>


              <Descriptions.Item
                label="商品说明"
              >
                <Space>
                  {
                    currentProduct.description
                    || "-"
                  }
                  {
                    editButton(
                      "description"
                    )
                  }
                </Space>
              </Descriptions.Item>


              <Descriptions.Item
                label="上架状态"
              >
                <Switch
                  checked={
                    currentProduct.enabled
                  }
                  onChange={() =>
                    toggleEnabled(
                      currentProduct
                    )
                  }
                />
              </Descriptions.Item>

            </Descriptions>

          )
        }

      </Modal>


      <Modal
        title={
          fieldTitle()
        }
        open={
          fieldOpen
        }
        onOk={
          saveField
        }
        onCancel={() => {

          setFieldOpen(
            false
          );

          setEditingField(
            null
          );

        }}
        okText="保存"
        cancelText="取消"
      >

        <Form
          form={
            fieldForm
          }
          layout="vertical"
        >
          {
            fieldEditor()
          }
        </Form>

      </Modal>


      <Modal
        title={
          currentOrder
            ? `订单详情 - ${currentOrder.order_no}`
            : "订单详情"
        }
        open={
          orderDetailOpen
        }
        footer={null}
        onCancel={() => {

          setOrderDetailOpen(
            false
          );

          setCurrentOrder(
            null
          );

        }}
        width={720}
      >

        {
          currentOrder
          && (

            <Descriptions
              bordered
              column={1}
            >

              <Descriptions.Item label="订单号">
                {currentOrder.order_no}
              </Descriptions.Item>

              <Descriptions.Item label="用户ID">
                {currentOrder.user_id}
              </Descriptions.Item>

              <Descriptions.Item label="商品">
                {currentOrder.product_name}
              </Descriptions.Item>

              <Descriptions.Item label="支付方式">
                {
                  paymentName(
                    currentOrder.payment_method
                  )
                }
              </Descriptions.Item>

              <Descriptions.Item label="蜗币金额">
                {currentOrder.coin_amount}
              </Descriptions.Item>

              <Descriptions.Item label="状态">
                {currentOrder.status}
              </Descriptions.Item>

              <Descriptions.Item label="创建时间">
                {
                  formatTime(
                    currentOrder.created_at
                  )
                }
              </Descriptions.Item>

              <Descriptions.Item label="支付时间">
                {
                  formatTime(
                    currentOrder.paid_at
                  )
                }
              </Descriptions.Item>

            </Descriptions>

          )
        }

      </Modal>


      <Modal
        title={
          currentGiftProduct
            ? `礼物详情 - ${currentGiftProduct.name}`
            : "礼物详情"
        }
        open={
          giftDetailOpen
        }
        footer={null}
        onCancel={() => {

          setGiftDetailOpen(
            false
          );

          setCurrentGiftProduct(
            null
          );

          setCurrentGiftConfig(
            null
          );

        }}
        width={720}
      >

        {
          currentGiftProduct
          && currentGiftConfig
          && (

            <Descriptions
              bordered
              column={1}
            >

              <Descriptions.Item
                label="礼物名称"
              >
                {
                  currentGiftProduct.name
                }
              </Descriptions.Item>


              <Descriptions.Item
                label="蜗币价格"
              >
                {
                  currentGiftProduct.coin_price
                }
              </Descriptions.Item>


              <Descriptions.Item
                label="稀有度"
              >
                <Space>
                  <Tag
                    color={
                      rarityColor(
                        currentGiftConfig.rarity
                      )
                    }
                  >
                    {
                      rarityName(
                        currentGiftConfig.rarity
                      )
                    }
                  </Tag>

                  {
                    giftEditButton(
                      "rarity"
                    )
                  }
                </Space>
              </Descriptions.Item>


              <Descriptions.Item
                label="经验奖励"
              >
                <Space>
                  {
                    currentGiftConfig.exp_reward
                  }

                  {
                    giftEditButton(
                      "exp_reward"
                    )
                  }
                </Space>
              </Descriptions.Item>


              <Descriptions.Item
                label="亲密度奖励"
              >
                <Space>
                  {
                    currentGiftConfig.intimacy_reward
                  }

                  {
                    giftEditButton(
                      "intimacy_reward"
                    )
                  }
                </Space>
              </Descriptions.Item>


              <Descriptions.Item
                label="礼物图标"
              >
                <Space>
                  {
                    currentGiftConfig.icon_url
                    || "-"
                  }

                  {
                    giftEditButton(
                      "icon_url"
                    )
                  }
                </Space>
              </Descriptions.Item>


              <Descriptions.Item
                label="上架状态"
              >
                <Switch
                  checked={
                    currentGiftProduct.enabled
                  }
                  onChange={() =>
                    toggleEnabled(
                      currentGiftProduct
                    )
                  }
                />
              </Descriptions.Item>

            </Descriptions>

          )
        }

      </Modal>


      <Modal
        title={
          giftFieldTitle()
        }
        open={
          giftFieldOpen
        }
        onOk={
          saveGiftField
        }
        onCancel={() => {

          setGiftFieldOpen(
            false
          );

          setGiftEditingField(
            null
          );

        }}
        okText="保存"
        cancelText="取消"
      >

        <Form
          form={
            giftFieldForm
          }
          layout="vertical"
        >
          {
            giftFieldEditor()
          }
        </Form>

      </Modal>


      <Modal
        title={
          currentGiftProduct
            ? `完成礼物配置 - ${currentGiftProduct.name}`
            : "完成礼物配置"
        }
        open={
          giftConfigOpen
        }
        onOk={
          saveGiftConfigCreate
        }
        onCancel={() => {

          setGiftConfigOpen(
            false
          );

        }}
        okText="保存"
        cancelText="取消"
      >

        <Form
          form={
            giftConfigForm
          }
          layout="vertical"
        >

          <Form.Item
            label="礼物图标地址"
            name="icon_url"
          >
            <Input />
          </Form.Item>


          <Form.Item
            label="稀有度"
            name="rarity"
          >
            <Select
              options={[
                {
                  label:"普通",
                  value:"normal"
                },
                {
                  label:"稀有",
                  value:"rare"
                },
                {
                  label:"史诗",
                  value:"epic"
                },
                {
                  label:"传说",
                  value:"legendary"
                }
              ]}
            />
          </Form.Item>


          <Form.Item
            label="经验奖励"
            name="exp_reward"
          >
            <InputNumber
              min={0}
              style={{
                width:"100%"
              }}
            />
          </Form.Item>


          <Form.Item
            label="亲密度奖励"
            name="intimacy_reward"
          >
            <InputNumber
              min={0}
              style={{
                width:"100%"
              }}
            />
          </Form.Item>

        </Form>

      </Modal>

    </Card>

  );

}
